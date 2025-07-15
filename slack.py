import requests
import os

from scrape import get_response

# SLACK_WEBHOOK_URL = "api"
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

if not SLACK_WEBHOOK_URL:
    raise ValueError("SLACK_WEBHOOK_URL environment variable is not set.")

def send_to_slack(message: str, webhook_url: str):
    payload = {"text": message}
    response = requests.post(webhook_url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")

if __name__ == "__main__":
    response = get_response()
    send_to_slack(response, SLACK_WEBHOOK_URL) 