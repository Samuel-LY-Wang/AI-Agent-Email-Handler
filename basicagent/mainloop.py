'''
Gmail API main script
'''

from scripts.check_email import check_email
from scripts.send_email import send_email
from scripts.openai_utils import draft_email, init_openai_client
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import logging

#authentication is a bit harder due to separate directories
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import base64
import urllib.parse
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

global SCOPES
with open("auth/SCOPE.json", "r") as f:
    SCOPES=json.load(f)["Scope"]

def decode(b64_encoded_str):
    decoded_data = base64.b64decode(b64_encoded_str)
    decoded_str = decoded_data.decode('utf-8')
    decoded_json=urllib.parse.unquote(decoded_str)
    return json.loads(decoded_json)

def draft_all_emails(user, user_info):
    '''
    The main loop
    Takes in a JSON config from the API
    Creates and drafts all emails
    '''
    global SCOPES
    # initialize OpenAI API client
    client = init_openai_client()
    # decode token from config
    token_b64 = user_info["token"]
    if isinstance(token_b64, list):
        token_b64 = token_b64[0]
    token_json = decode(token_b64)
    with open(f"auth/tokens/token_{user}.json", "w") as f:
        json.dump(token_json, f)
    creds = Credentials.from_authorized_user_file(f'auth/tokens/token_{user}.json', SCOPES)
    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    email_address = profile['emailAddress']
    #verify that authenticated email matches expected user
    if (email_address != user):
        logging.info(f"WARNING: Authenticated email {email_address} does not match expected {user}")
    else:
        logging.info(f"Authenticated {email_address} successfully.")
    # check email
    emails = check_email(user, service, user_info)

    # draft replies and send them
    if emails:
        for email in emails:
            msg = draft_email(client, email, user_info)
            logging.info(f"Drafted email for {email.sender} with subject '{email.subject}'")
            send_email(service, msg, user_info)
        logging.info("All emails sent successfully.")
    else:
        logging.info(f"No emails found for {email_address}.")
    service.close() # close service to avoid memory leak

if __name__=="__main__":
    user_info={
        "token": "[redacted]",
        "mode": "blacklist",
        "blacklist": [],
        "whitelist": [],
        "relation": {}
    }
    draft_all_emails("samuellywang@gmail.com", user_info)