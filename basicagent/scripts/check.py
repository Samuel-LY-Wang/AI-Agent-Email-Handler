from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from scripts.get_msg_body import *
from scripts.SCOPE import SCOPES
from datetime import datetime

def get_cur_time():
    '''
    gets the current date in YYYY/MM/DD format and returns a query string for Gmail API.\n
    The query string is formatted as "after:YYYY/MM/DD" to filter emails received today'''
    today = datetime.today().strftime('%Y/%m/%d')
    query = f"after:{today}"
    return query

def check_email():
    '''
    Checks Gmail for all emails received today in Primary or Inbox\n
    Returns each email as a list:\n
    [message id, thread id, subject, sender, date, body]'''
    creds = Credentials.from_authorized_user_file('auth/token.json', SCOPES)

    # Build Gmail API service
    service = build('gmail', 'v1', credentials=creds)

    # Call Gmail API to get the 10 most recent emails
    results = service.users().messages().list(userId='me', labelIds=['INBOX', 'CATEGORY_PERSONAL'], q=get_cur_time()).execute()
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
            emails.append([msg_id, thread_id, subject, sender, date, body])
            # print("Subject:", subject)
            # print("Headers:", headers)
            # print("Message ID:", msg['id'])
            # print("Snippet:", msg_data.get('snippet', 'No snippet available'))
            print("-" * 40)
    return emails