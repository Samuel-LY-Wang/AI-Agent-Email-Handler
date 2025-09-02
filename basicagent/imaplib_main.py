'''
Deprecated script for checking emails with IMAP.\n
Not useful for the current gmail-only scope, but the "check" script may be reused for a provider-agnostic handler.
'''

raise ValueError("Script is now deprecated, please ignore")

from openai import OpenAI
import email
from email.header import decode_header
import imaplib
from dotenv import dotenv_values
from datetime import *
import html

env_vars=dotenv_values(".env")
API_KEY=env_vars["OPEN_API_KEY"]
client = OpenAI(api_key=API_KEY)
uname=env_vars["EMAIL"]
pword=env_vars["EMAIL_PASS"]

i=imaplib.IMAP4_SSL("imap.gmail.com")

i.login(uname, pword)

def check_email():
    emails=[]
    t=datetime.now().strftime("%d-%b-%Y")
    # print(t)
    i.select('"[Gmail]/All Mail"')
    status, messages = i.search(None, f'SINCE {t}')
    print("Status: ",status)
    ids=messages[0].split()
    print(f"Found {len(ids)} messages")
    print("Message ids: ",ids)
    one_hr_ago=datetime.now(timezone.utc)-timedelta(hours=1)
    for id in ids:
        status, msg_data = i.fetch(id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Parse the date from the email
        email_time = email.utils.parsedate_to_datetime(msg["Date"])
        email_time=email_time.astimezone(timezone.utc)
        # print(email_time)
        # print(one_hr_ago)
        if email_time:
            # Decode subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")

            from_ = msg.get("From")

            # print(f"From: {from_}")
            # print(f"Subject: {subject}")
            # print(f"Date: {email_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")

            # Get body (only text/plain for simplicity)
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                        body = part.get_payload(decode=True).decode(errors="replace")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="replace")
            body=body.replace('\r\n','\n').replace('\r','\n')
            emails.append([id, from_, subject, html.unescape(body)])

            # print("Body Preview:", body[:200], "\n---\n")
    return emails


def send_email(FROM, TO, SUBJECT, BODY):
    #todo: write the draft email logic
    pass

emails=check_email()
print(emails)
for msg in emails:
    out_from=uname
    out_to=msg[1]
    try:
        out_body=client.responses.create(model="gpt-4.1-mini", input=f"Write a response to an email from {out_to}, {RELATION[out_to]}. The email I received has subject {msg[2]} and body text {msg[3]}")
    except KeyError:
        out_body=client.responses.create(model="gpt-4.1-mini", input=f"Write a response to an email from {out_to}. The email I received has subject {msg[2]} and body text {msg[3]}")
    out_subject=f"Re: {msg[2]}"
    send_email(out_from, out_to, out_subject, out_body)
# print(emails)
# for msg in emails:
#     print(msg)

# response = client.responses.create(
#     model="gpt-4.1-mini",
#     input="Write a one-sentence bedtime story about a unicorn."
# )

# print(response.output_text)