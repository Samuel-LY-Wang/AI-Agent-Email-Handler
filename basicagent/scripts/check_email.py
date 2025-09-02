'''
All scripts necessary to check the email via gmail API
'''

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from scripts.parse_msg import *
from datetime import datetime
from scripts.email_class import Email

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import *

def accept_email(cur_email, msg, mode=PREFERRED_MODE):
    '''
    Params:\n
    cur_email (the email that is in use right now)\n
    msg (the email as a list)\n
    Takes in an email and decides whether to accept or reject based on sender\n
    Has 2 different modes:\n
    Blacklist mode (default): accepts all emails except those from blacklisted senders\n
    Whitelist mode: only accepts emails from whitelisted senders'''
    sender=msg[3].split(" ")[-1]
    sender.strip("<>") # remove <> tags gmail places sometimes
    if (cur_email == sender):
        # never replies to your own emails
        return False
    if (mode=='blacklist'):
        # if the sender is in the blacklist, return False
        if sender in BLACKLIST.get(cur_email, []):
            return False
        # otherwise, return True
        return True
    elif (mode=='whitelist'):
        # if the sender is in the whitelist, return True
        if sender in WHITELIST.get(cur_email, []):
            return True
        # otherwise, return False
        return False

def get_cur_time():
    '''
    gets the current date in YYYY/MM/DD format and returns a query string for Gmail API.\n
    The query string is formatted as "after:YYYY/MM/DD" to filter emails received today'''
    today = datetime.today().strftime('%Y/%m/%d')
    query = f"after:{today}"
    return query

def check_email(user, service):
    '''
    Checks Gmail for all emails received today in Primary or Inbox\n
    Limit of 10 emails due to API restrictions.\n
    Returns each email as an Email object with attributes:\n
    Message ID, Thread ID, Subject, Sender, Date, Body text'''

    # Call Gmail API to get the 10 most recent emails, only including Primary/Inbox emails today
    results = service.users().messages().list(userId='me', labelIds=['INBOX', 'CATEGORY_PERSONAL'], q=get_cur_time(), maxResults=10).execute()
    messages = results.get('messages', [])
    # print(messages)
    emails=[]
    if not messages:
        return None
    else:
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            msg_id = msg_data['id']
            thread_id = msg_data['threadId']
            headers = msg_data['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "(No Sender)")
            date = next((h['value'] for h in headers if h['name'] == 'Date'), "(No Date)")
            body = get_message_body(msg_data)
            email=[msg_id, thread_id, subject, sender, date, body]
            #strips leading and trailing whitespace to make life easier.
            email = [attribute.strip() if isinstance(attribute, str) else attribute for attribute in email]
            # print(email)
            #decide whether to reply based on the blacklist, whitelist, and preferred mode
            if accept_email(user, email):
                new_email=Email(msg_id=msg_id, thd_id=thread_id, subject=subject, sender=sender, date=date, body=body)
                emails.append(new_email)
            # Debug print statements, ignore
            # print(sender)
            # print("Subject:", subject)
            # print("Headers:", headers)
            # print("Message ID:", msg['id'])
            # print("Snippet:", msg_data.get('snippet', 'No snippet available'))
            # print("-" * 40)
    return emails