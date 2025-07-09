from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from scripts.get_msg_body import *
from scripts.SCOPE import SCOPES
from datetime import datetime

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import *

def accept_email(msg, mode=PREFERRED_MODE):
    '''
    Takes in an email and decides whether to accept or reject based on sender\n
    Has 2 different modes:\n
    Blacklist mode (default): accepts all emails except those from blacklisted senders\n
    Whitelist mode: only accepts emails from whitelisted senders'''
    if (mode=='blacklist'):
        # if the sender is in the blacklist, return False
        if msg[3] in BLACKLIST:
            return False
        # otherwise, return True
        return True
    elif (mode=='whitelist'):
        # if the sender is in the whitelist, return True
        if msg[3] in WHITELIST:
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

def check_email(user):
    '''
    Checks Gmail for all emails received today in Primary or Inbox\n
    Limit of 10 emails due to API restrictions.\n
    Returns each email as a list:\n
    [message id, thread id, subject, sender, date, body]'''
    creds = Credentials.from_authorized_user_file(f'auth/tokens/token_{user}.json', SCOPES)

    # Build Gmail API service
    service = build('gmail', 'v1', credentials=creds)

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
            for attribute in email:
                attribute = attribute.strip() if isinstance(attribute, str) else attribute
            #decide whether to reply based on the blacklist, whitelist, and preferred mode
            if accept_email(email):
                emails.append([msg_id, thread_id, subject, sender, date, body])
            # Debug print statements, ignore
            # print(sender)
            # print("Subject:", subject)
            # print("Headers:", headers)
            # print("Message ID:", msg['id'])
            # print("Snippet:", msg_data.get('snippet', 'No snippet available'))
            # print("-" * 40)
    return emails