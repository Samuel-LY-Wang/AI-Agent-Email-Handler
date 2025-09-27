import base64
import json
import urllib.parse
import os
import stat

def decode_and_save_token(user, token_field):
    """
    Accepts user (email) and token_field which can be:
      - a base64-encoded string containing the credentials JSON
      - a URL-encoded JSON string
      - a raw JSON string
      - a list with the token string as first element
    Writes credentials to auth/tokens/token_{user}.json and returns the path.
    Raises ValueError on invalid input.
    If token_field is None and a token file already exists, returns existing path.
    """
    # determine token directory relative to repository root: ../../auth/tokens from this file
    token_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'auth', 'tokens'))
    os.makedirs(token_dir, exist_ok=True)
    token_path = os.path.join(token_dir, f"token_{user}.json")

    if not token_field:
        # no token provided: if token file exists, return it, else error
        if os.path.exists(token_path):
            return token_path
        raise ValueError("No token provided and no existing token file found.")

    # if token is provided as a list, grab first element
    if isinstance(token_field, list):
        token_field = token_field[0]

    # try URL-unquote first
    try:
        maybe = urllib.parse.unquote(token_field)
    except Exception:
        maybe = token_field

    decoded = None
    # Heuristic: if it doesn't look like JSON, try base64 decode
    try:
        if '{' not in maybe[:50]:
            decoded_bytes = base64.b64decode(maybe)
            decoded = decoded_bytes.decode('utf-8')
        else:
            decoded = maybe
    except Exception:
        decoded = maybe

    # final attempt to parse JSON
    parsed = None
    try:
        parsed = json.loads(decoded)
    except Exception:
        try:
            parsed = json.loads(urllib.parse.unquote(decoded))
        except Exception:
            raise ValueError("Token field could not be decoded as JSON credentials.")

    # basic validation
    if not isinstance(parsed, dict) or not any(k in parsed for k in ("token", "refresh_token", "access_token", "client_id")):
        raise ValueError("Decoded token JSON doesn't look like OAuth credentials.")

    # write to file with secure permissions
    with open(token_path, 'w') as f:
        json.dump(parsed, f)
    try:
        os.chmod(token_path, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    except Exception:
        # ignore permission change failures on platforms that don't support chmod
        pass

    return token_path
