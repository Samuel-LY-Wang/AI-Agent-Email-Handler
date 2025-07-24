FROM python:3.13-slim

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "basicagent/gmail_api_main.py"]