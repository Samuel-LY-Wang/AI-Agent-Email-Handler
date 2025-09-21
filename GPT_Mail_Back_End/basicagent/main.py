from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from google_auth_oauthlib.flow import Flow
import os
import pathlib
import uvicorn
import logging
import json
from mainloop import draft_all_emails

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Google OAuth2 setup
GOOGLE_CLIENT_SECRETS_FILE = os.path.join(pathlib.Path(__file__).parent.parent, "auth", "credentials.json")
with open("config.json", "r") as f:
    config=json.load(f)
    GOOGLE_SCOPES = config["Scope"]
    MAIN_URL=config["URL"]
GOOGLE_REDIRECT_URI = f"{MAIN_URL}/auth/callback"

@app.get("/auth/google")
async def google_auth():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=GOOGLE_SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline", include_granted_scopes="true")
    return RedirectResponse(auth_url)

@app.get("/auth/callback")
async def google_auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse(content={"status": "error", "message": "No code provided"}, status_code=400)
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=GOOGLE_SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials
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
    token_path = f"auth/tokens/token_{user_email}.json"
    with open(token_path, "w") as f:
        f.write(credentials.to_json())
    return JSONResponse(content={"status": "success", "email": user_email})

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
        for user in data:
            if not has_all_expected_inputs(data[user], expected_inputs):
                return JSONResponse(content={"status": "error", "message": f"Not all values were included! User {user} was missing some fields"}, status_code=400)
            draft_all_emails(user, data[user])
        return JSONResponse(content={}, status_code=204)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)