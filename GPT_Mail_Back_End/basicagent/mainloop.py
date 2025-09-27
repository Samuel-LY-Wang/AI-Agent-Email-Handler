'''
Gmail API main script
'''

from scripts.check_email import check_email
from scripts.send_email import send_email
from scripts.openai_utils import draft_email, init_openai_client
from scripts.token_utils import decode_and_save_token
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
import stat

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def draft_all_emails(user, user_info):
    '''
    The main loop
    Takes in a JSON config from the API
    Creates and drafts all emails
    '''
    # initialize OpenAI API client
    client = init_openai_client()
    # decode/save token from user_info (if provided) and load credentials
    token_path = decode_and_save_token(user, user_info.get('token'))
    try:
        creds = Credentials.from_authorized_user_file(token_path)
    except Exception as e:
        # If the token file is invalid or expired, surface a helpful error
        raise ValueError(f"Failed to load credentials for {user}: {e}. You may need to re-authenticate via /auth/google.")
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
    drafted_count = 0
    if emails:
        for email in emails:
            msg = draft_email(client, email, user_info)
            logging.info(f"Drafted email for {email.sender} with subject '{email.subject}'")
            send_email(service, msg, user_info)
            drafted_count += 1
        logging.info("All emails sent successfully.")
    else:
        logging.info(f"No emails found for {email_address}.")
    service.close() # close service to avoid memory leak

    # return a small summary so callers (e.g. API) can report success/count
    return {"user": user, "drafted": drafted_count}

# just for the purpose of testing, ignore
# if __name__=="__main__":
#     user_info={
#         "token": "[redacted]",
#         "mode": "blacklist",
#         "blacklist": [],
#         "whitelist": [],
#         "relation": {}
#     }
#     draft_all_emails("samuellywang@gmail.com", user_info)