from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from google_auth_oauthlib.flow import Flow
import os
import pathlib
import uvicorn
import logging
import json
import urllib.parse
from mainloop import draft_all_emails
from googleapiclient.errors import HttpError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Google OAuth2 setup
GOOGLE_CLIENT_SECRETS_FILE = os.path.join(pathlib.Path(__file__).parent.parent, "auth", "credentials.json")
with open("config.json", "r") as f:
    config=json.load(f)
    GOOGLE_SCOPES = config["Scope"]
    MAIN_URL=config["URL"]
    FRONTEND_URL = config.get("FRONTEND_URL", "http://127.0.0.1:5173")
GOOGLE_REDIRECT_URI = f"{MAIN_URL}/auth/callback"

@app.get("/auth/google")
async def google_auth(request: Request):
    # compute redirect_uri based on current request to avoid mismatch
    origin = str(request.base_url).rstrip('/')
    redirect_uri = f"{origin}/auth/callback"
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=GOOGLE_SCOPES,
        redirect_uri=redirect_uri
    )
    # Do not use include_granted_scopes=True here; if Google adds previously granted scopes
    # (e.g. gmail.readonly) the subsequent token exchange can fail with invalid_grant.
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    return RedirectResponse(auth_url)

@app.get("/auth/callback")
async def google_auth_callback(request: Request):
    # compute redirect_uri used in the auth step
    origin = str(request.base_url).rstrip('/')
    redirect_uri = f"{origin}/auth/callback"
    code = request.query_params.get("code")
    if not code:
        return JSONResponse(content={"status": "error", "message": "No code provided"}, status_code=400)
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=GOOGLE_SCOPES,
        redirect_uri=redirect_uri
    )
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
    except Exception as e:
        # log detailed error server-side
        logging.exception("Token exchange failed")
        # map provider errors to safe keys
        err_text = str(e)
        if "invalid_grant" in err_text:
            err_key = "auth_invalid_grant"
        elif "access_denied" in err_text or "consent_required" in err_text:
            err_key = "auth_denied"
        else:
            err_key = "auth_failed"
        qs = urllib.parse.urlencode({"error": err_key})
        return RedirectResponse(f"{FRONTEND_URL}/?{qs}")
    # Use access token to get user email from Google's userinfo endpoint
    import requests
    userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {credentials.token}"}
    resp = requests.get(userinfo_endpoint, headers=headers)
    if resp.status_code != 200:
        return JSONResponse(content={"status": "error", "message": "Failed to fetch user info.", "error": resp.content}, status_code=resp.status_code)
    userinfo = resp.json()
    user_email = userinfo.get("email")
    if not user_email:
        return JSONResponse(content={"status": "error", "message": "Could not retrieve user email from userinfo."}, status_code=400)
    token_path = f"GPT_Mail_Back_End/auth/tokens/token_{user_email}.json"
    with open(token_path, "w") as f:
        f.write(credentials.to_json())

    # warn if refresh_token is not present (Google may not return it if previously granted)
    refresh_token_present = getattr(credentials, 'refresh_token', None) is not None
    params = {"email": user_email}
    if not refresh_token_present:
        params["warning"] = "no_refresh_token"
    qs = urllib.parse.urlencode(params)
    redirect_to = f"{FRONTEND_URL}/?{qs}"
    return RedirectResponse(redirect_to)

def has_all_expected_inputs(dict, inputs):
    dict_keys=set(dict.keys())
    for param in inputs:
        if param not in dict_keys:
            return False
    return True

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run-agent")
async def run_agent(request: Request):
    expected_inputs=["mode", "blacklist", "whitelist", "relation"]
    try:
        data = await request.json()
        '''
        Data should be of the form:
        {
            'user':
            {
                'mode': ('blacklist' or 'whitelist'),
                'blacklist': list of blacklisted accounts,
                'whitelist': list of whitelisted accounts
                'relation': relations
            }, (a dict for each user)
        }
        '''
        results = []
        for user in data:
            # ensure each user has the expected inputs; record per-user error instead of failing all
            if not has_all_expected_inputs(data[user], expected_inputs):
                results.append({"user": user, "status": "error", "error": "missing_fields", "message": f"Not all values were included for user {user}"})
                continue
            try:
                res = draft_all_emails(user, data[user])
                # normalize the success shape
                results.append({"user": user, "status": "success", "drafted": res.get("drafted", 0)})
            except ValueError as e:
                # likely credential loading or validation issue raised from mainloop
                err_text = str(e)
                if "Failed to load credentials" in err_text:
                    err_key = "user_not_authenticated"
                else:
                    err_key = "credentials_load_failed"
                logging.exception("Credential error for user %s", user)
                results.append({"user": user, "status": "error", "error": err_key, "message": err_text})
            except HttpError as e:
                # map common Gmail API http errors to safe keys
                try:
                    status_code = int(e.resp.status)
                except Exception:
                    status_code = None
                logging.exception("Gmail API error for user %s", user)
                if status_code == 404:
                    err_key = "invalid_user_email"
                elif status_code == 403:
                    err_key = "permission_denied"
                else:
                    err_key = "gmail_api_error"
                results.append({"user": user, "status": "error", "error": err_key, "message": str(e)})
            except Exception as e:
                logging.exception("Unexpected error running agent for user %s", user)
                results.append({"user": user, "status": "error", "error": "agent_failed", "message": str(e)})
        # overall response always 200 with per-user statuses so frontend can render friendly messages per user
        return JSONResponse(content={"status": "ok", "results": results}, status_code=200)
    except Exception as e:
        logging.exception("Failed to parse /run-agent request")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=400)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)