'''
This is the script that allows you to authenticate your gmail account.
'''

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
import os

SCOPES=['https://www.googleapis.com/auth/gmail.modify']

def is_valid_token(token):
    '''
    Checks if the token is valid by trying to build the gmail service with it.
    Returns True if the token is valid, False otherwise.
    '''
    if not os.path.exists(token):
        # the token file does not exist, so invalid
        return False
    creds = Credentials.from_authorized_user_file(token, SCOPES)
    if creds and creds.valid:
        return True
    elif creds and creds.expired and creds.refresh_token:
        # try to refresh token
        try:
            creds.refresh(Request())
            with open(token, 'w') as token_file:
                token_file.write(creds.to_json())
            return True
        except RefreshError as e:
            print("Refresh token is no longer valid. Please re-authenticate.")
            return False
    else:
        return False

def authenticate_gmail(uname):
    '''
    Opens a window asking user to log into their email\n
    IMPORTANT: YOU MUST LOG IN WITH THE RIGHT EMAIL!\n
    PLEASE LOG INTO ALL YOUR ACCOUNTS IN THE RIGHT ORDER!\n
    stores the authentication token in auth/tokens/token_{email}.json
    '''
    token_file=f'auth/tokens/token_{uname}.json'
    if is_valid_token(token_file):
        # token is valid, no need to re-authenticate
        return
    flow = InstalledAppFlow.from_client_secrets_file('auth/credentials.json', SCOPES)
    creds = flow.run_local_server(port=0, access_type='offline', prompt='consent')
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