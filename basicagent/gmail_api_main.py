from openai import OpenAI
from dotenv import dotenv_values
from datetime import *
from relations import RELATION
import os.path
import base64
import email
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# IMPORTANT: THIS ASSUMES YOU HAVE VALID CREDENTIALS. IF NOT, PLEASE FIRST RUN auth.py

env_vars=dotenv_values(".env")
API_KEY=env_vars["OPEN_API_KEY"]
client = OpenAI(api_key=API_KEY)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    flow = InstalledAppFlow.from_client_secrets_file('basicagent/credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Save credentials for future runs
    with open('auth/token.json', 'w') as token:
        token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def check_email():
    creds = Credentials.from_authorized_user_file('auth/token.json', SCOPES)

    # Build Gmail API service
    service = build('gmail', 'v1', credentials=creds)

    # Call Gmail API to get the 10 most recent emails
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])
    # print(messages)
    emails=[]
    if not messages:
        print("No messages found.")
    else:
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            headers = msg_data['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
            sender= next((h['value'] for h in headers if h['name'] == 'From'), "(No Sender)")
            date= next((h['value'] for h in headers if h['name'] == 'Date'), "(No Date)")
            emails.append([subject, sender, date, msg_data])
            print("Subject:", subject)
            # print("Headers:", headers)
            print("Message ID:", msg['id'])
            # print("Snippet:", msg_data.get('snippet', 'No snippet available'))
            print("-" * 40)
    return emails


def send_email(FROM, TO, SUBJECT, BODY):
    #todo: write the draft email logic
    pass

authenticate_gmail()
emails=check_email()
# print(emails)
# for msg in emails:
#     print(msg)

# response = client.responses.create(
#     model="gpt-4.1-mini",
#     input="Write a one-sentence bedtime story about a unicorn."
# )

# print(response.output_text)