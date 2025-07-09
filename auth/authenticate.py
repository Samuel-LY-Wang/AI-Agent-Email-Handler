from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from googleapiclient.discovery import build
from basicagent.scripts.SCOPE import SCOPES

def authenticate_gmail(uname):
    '''
    Opens a window asking user to log into their email\n
    IMPORTANT: YOU MUST LOG IN WITH THE RIGHT EMAIL!\n
    PLEASE LOG INTO ALL YOUR ACCOUNTS IN THE RIGHT ORDER!\n
    stores the authentication token in auth/tokens/token_{email}.json'''
    token_file=f'auth/tokens/token_{uname}.json'
    flow = InstalledAppFlow.from_client_secrets_file('basicagent/credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    # print(creds_json["account"])

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save credentials
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)