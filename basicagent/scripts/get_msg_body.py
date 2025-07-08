import base64

def extract_text_from_parts(parts):
    message_body = ""

    for part in parts:
        filename = part.get('filename')
        body = part.get('body', {})
        mime_type = part.get('mimeType')
        data = body.get('data')

        # Skip attachments
        if filename:
            continue

        # If it's plain text or HTML, decode it
        if data and mime_type in ['text/plain', 'text/html']:
            message_body += decode_base64(data)

        # If nested parts exist, recurse
        if 'parts' in part:
            message_body += extract_text_from_parts(part['parts'])

    return message_body

def decode_base64(data):
    return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')

def get_message_body(msg):
    payload = msg.get('payload', {})

    # Case 1: Body directly in payload
    if 'data' in payload.get('body', {}):
        return decode_base64(payload['body']['data'])

    # Case 2: Body in MIME parts
    elif 'parts' in payload:
        return extract_text_from_parts(payload['parts'])

    return "(No body found)"