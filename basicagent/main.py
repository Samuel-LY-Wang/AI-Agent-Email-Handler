from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from mainloop import draft_all_emails

def has_all_expected_inputs(dict, inputs):
    dict_keys=set(dict.keys())
    for param in inputs:
        if param not in dict_keys:
            return False
    return True

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run-agent")
async def run_agent(request: Request):
    expected_inputs=["token", "mode", "blacklist", "whitelist", "relation"]
    try:
        data = await request.json()
        '''
        Data should be of the form:
        {
            'user':
            {
                'token': (base64 encoded token),
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