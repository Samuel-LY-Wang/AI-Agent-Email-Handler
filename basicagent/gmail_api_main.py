from openai import OpenAI
from dotenv import dotenv_values
from relations import RELATION
from scripts.check import *
from scripts.get_msg_body import *
from scripts.send import *

#authentication is a bit harder due to separate directories
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from auth.authenticate import *

# initialize Gmail API client
authenticate_gmail()
creds = Credentials.from_authorized_user_file('auth/token.json', SCOPES)
service = build('gmail', 'v1', credentials=creds)

# initialize OpenAI API client
env_vars=dotenv_values(".env")
API_KEY=env_vars["OPEN_API_KEY"]
client = OpenAI(api_key=API_KEY)

# check email
emails=check_email()

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
    print("No emails found.")