from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from scripts.SCOPE import SCOPES

def authenticate_gmail():
    flow = InstalledAppFlow.from_client_secrets_file('basicagent/credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Save credentials for future runs
    with open('auth/token.json', 'w') as token:
        token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)