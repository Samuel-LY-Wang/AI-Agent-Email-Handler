'''
Gmail API main script
'''

from openai import OpenAI
from dotenv import dotenv_values
from relations import RELATION
from scripts.check import *
from scripts.get_msg_body import *
from scripts.send import *
from config import *
import warnings

#authentication is a bit harder due to separate directories
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from auth.authenticate import *

print("Remember to authenticate your account in the right order! Here is the order:")
for i in range(len(LOGIN_USERS)):
    print(f"{i+1}: {LOGIN_USERS[i]}")

# initialize OpenAI API client
env_vars=dotenv_values(".env")
API_KEY=env_vars["OPEN_API_KEY"]
client = OpenAI(api_key=API_KEY)

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
        warnings.warn(f"WARNING: Authenticated email {email_address} does not match expected {user}", RuntimeWarning)
    else:
        print(f"Authenticated {email_address} successfully.")
    # check email
    emails=check_email(user)

    # draft replies and send them
    if emails:
        # each email is [message_id, thread_id, subject, sender, date, body]
        for email in emails:
            msg_id, thd_id, subject, sender, date, body = email
            if sender in RELATION:
                relation = RELATION[sender]
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=f"Draft an email responding to the email '{subject}' from {relation} ({sender}). The body of the email is: {body}"
                )

            else:
                relation = None
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=f"Draft an email responding to the email '{subject}' from {sender}. The body of the email is: {body}"
                )
            #sends email with correct syntax
            send_email(service=service, in_reply_to=sender, subject=f"Re: {subject}", body_text=response.output_text, thread_id=thd_id, message_id=msg_id)
            print("All emails sent successfully.")
    else:
        # this just means emails=None
        # this is fine
        print(f"No emails found for {email_address}.")
    service.close() # close service to avoid memory leak

#close the OpenAI client
#done last since one is used for all users
client.close()