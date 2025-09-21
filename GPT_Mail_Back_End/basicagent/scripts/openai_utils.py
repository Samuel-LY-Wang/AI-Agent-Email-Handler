from openai import OpenAI
from dotenv import dotenv_values
from scripts.email_class import Email

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def init_openai_client():
    """
    Initialize the OpenAI API client with the API key from environment variables.
    """
    env_vars = dotenv_values(".env")
    api_key = env_vars.get("OPEN_API_KEY")
    if not api_key:
        raise ValueError("OPEN_API_KEY not found in .env file.")
    
    return OpenAI(api_key=api_key)

def draft_email(client, email, config):
    """
    Draft an email response using OpenAI's API.
    
    :param client: OpenAI API client
    :param email: An Email object containing all email data
    :return: Drafted email as object
    """
    relation=config["relation"].get(email.sender, None)
    if relation:
        prompt = f"You are a model that is very good at writing professional emails. Draft an email responding to the email '{email.subject}' from {relation} ({email.sender}). The body of the email is: {email.body}. Please do not include a subject line."
    else:
        prompt = f"You are a model that is very good at writing professional emails. Draft an email responding to the email '{email.subject}' from {email.sender}. The body of the email is: {email.body}. Please do not include a subject line."
    
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    new_email=email.create_new({"body": response.output_text, "subject": f"Re: {email.subject}"})
    
    return new_email