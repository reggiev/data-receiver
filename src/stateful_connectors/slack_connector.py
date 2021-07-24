import requests
import os


def get_webhook_url(channel):
    return os.environ.get(channel, "")


def send_msg_to_slack_channel(channel, json):
    return
    headers = {
        'Content-type': 'application/json',
    }

    url = get_webhook_url(channel)
    response = requests.post(url, headers=headers, json=json)
    print("Slack message response code: " + str(response.status_code))
