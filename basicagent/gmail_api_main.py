'''
Gmail API main script
'''

from scripts.check_email import *
from scripts.parse_msg import *
from scripts.send_email import *
from scripts.openai_utils import *
from config import *
import logging

#authentication is a bit harder due to separate directories
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from auth.authenticate import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# initialize OpenAI API client
client = init_openai_client()

# initialize Gmail API client for each user
for user in LOGIN_USERS:
    # authenticate user
    authenticate_gmail(user)
    #initialize Gmail API service
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
    emails=check_email(user, service)

    # draft replies and send them
    if emails:
        # each email is [message_id, thread_id, subject, sender, date, body]
        for email in emails:
            msg_id, thd_id, subject, sender, date, body = email
            msg = draft_email(client, subject, sender, body, relation=RELATION.get(sender))
            logging.info(f"Drafted email for {sender} with subject '{subject}'")
            #sends email with correct syntax
            send_email(service=service, in_reply_to=sender, subject=f"Re: {subject}", body_text=msg, thread_id=thd_id, message_id=msg_id)
        logging.info("All emails sent successfully.")
    else:
        # this just means emails=None
        # this is fine
        logging.info(f"No emails found for {email_address}.")
    service.close() # close service to avoid memory leak

#close the OpenAI client
#done last since one is used for all users
client.close()