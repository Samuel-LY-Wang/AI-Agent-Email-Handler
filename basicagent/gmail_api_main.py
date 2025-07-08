from openai import OpenAI
from dotenv import dotenv_values
from relations import RELATION
from scripts import *
from scripts.authenticate import *
from scripts.check import *
from scripts.get_msg_body import *
from scripts.send import *

env_vars=dotenv_values(".env")
API_KEY=env_vars["OPEN_API_KEY"]
client = OpenAI(api_key=API_KEY)

authenticate_gmail()
emails=check_email()
try:
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
        send_email(TO=sender, SUBJECT=f"Re: {subject}", BODY=response.output_text, MSG_ID=msg_id, THD_ID=thd_id)
        print("All emails sent successfully.")
except:
    print("No emails found.")
    exit(0)
# print(emails)
# for msg in emails:
#     print(msg)

# response = client.responses.create(
#     model="gpt-4.1-mini",
#     input="Write a one-sentence bedtime story about a unicorn."
# )

# print(response.output_text)