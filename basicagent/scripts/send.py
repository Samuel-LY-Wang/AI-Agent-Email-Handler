import base64
from email.message import EmailMessage

def create_reply_message(subject, in_reply_to, thread_id, body_text):
    '''
    creates a reply message in the required format for Gmail API.\n
    Returns a dictionary with the message body and metadata.'''
    message = EmailMessage()
    message.set_content(body_text)
    message['To'] = in_reply_to
    message['Subject'] = subject if subject.startswith("Re:") else f"Re: {subject}"
    message['In-Reply-To'] = in_reply_to
    message['References'] = in_reply_to
    message['From'] = "me"  # this tells the Gmail API to use the authenticated user
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    return {
        'message': {
            'raw': raw_message,
            'threadId': thread_id
        }
    }

def send_email(service, subject, in_reply_to, thread_id, body_text):
    '''
    Sends a reply email to the specified recipient and saves it as a draft.'''
    draft = create_reply_message(subject, in_reply_to, thread_id, body_text)
    try:
        response = service.users().drafts().create(userId='me', body=draft).execute()
        print(f"Draft created with ID: {response['id']}")
        return response
    except Exception as e:
        print(f"An error occurred while saving the draft: {e}")
        return None