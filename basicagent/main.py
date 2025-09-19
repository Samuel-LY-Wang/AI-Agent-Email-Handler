from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from mainloop import mainloop

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
    expected_inputs=["users", "mode", "blacklist", "whitelist", "relation"]
    try:
        data = await request.json()
        '''
        Data should be of the form:
        {
            'users': [list of users]
            'mode': either 'blacklist' or 'whitelist'
            'blacklist': blacklisted accounts
            'whitelist': whitelisted accounts
            'relation': relations between the user and others
        }
        '''
        if not has_all_expected_inputs(data, expected_inputs):
            return JSONResponse(content={"status": "error", "message": "Not all values were included!"}, status_code=400)
        result = mainloop(data)
        return JSONResponse(content={"status": "success", "result": result})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)