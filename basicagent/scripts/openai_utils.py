from openai import OpenAI
from dotenv import dotenv_values

def init_openai_client():
    """
    Initialize the OpenAI API client with the API key from environment variables.
    """
    env_vars = dotenv_values(".env")
    api_key = env_vars.get("OPEN_API_KEY")
    if not api_key:
        raise ValueError("OPEN_API_KEY not found in .env file.")
    
    return OpenAI(api_key=api_key)

def draft_email(client, subject, sender, body, relation=None):
    """
    Draft an email response using OpenAI's API.
    
    :param client: OpenAI API client
    :param subject: Subject of the email to respond to
    :param sender: Sender of the email
    :param body: Body of the email to respond to
    :param relation: Relation to the sender (optional)
    :return: Drafted email response text
    """
    if relation:
        prompt = f"Draft an email responding to the email '{subject}' from {relation} ({sender}). The body of the email is: {body}"
    else:
        prompt = f"Draft an email responding to the email '{subject}' from {sender}. The body of the email is: {body}"
    
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    
    return response.output_text