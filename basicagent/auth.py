from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle

# Scope needed for reading and writing drafts
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    flow = InstalledAppFlow.from_client_secrets_file('basicagent/credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Save credentials for future runs
    with open('token.pkl', 'wb') as token:
        pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

authenticate_gmail()