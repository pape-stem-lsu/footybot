from flask import Flask, request
import requests
import schedule
import time
from threading import Thread
from datetime import datetime
import os
import json

app = Flask(__name__)

BOT_ID = "4b86ded6c239105623a8a243c6"
GROUP_ID = "103943618"
ACCESS_TOKEN = "dzIrDPvokcfyTAeoj5YA0j5xBR7wY66ySboWso1t"

os.environ['TZ'] = 'America/Chicago'

def create_poll():
    url = f"https://api.groupme.com/v3/polls/{GROUP_ID}"
    headers = {
        "X-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    
    poll_data = {
        "poll": {
            "subject": "Are you pulling up today?",
            "options": [
                {"title": "yes"},
                {"title": "no"},
                {"title": "#?"}
            ],
            "expiration": 86400,
            "type": "single"
        }
    }
    
    print(f"Creating poll at {datetime.now()}")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(poll_data)}")
    
    try:
        response = requests.post(url, json=poll_data, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 201:
            poll_response = response.json()
            poll_id = poll_response['poll']['id']
            print(f"Poll ID: {poll_id}")
            send_message_with_poll(poll_id)
        else:
            print(f"Failed to create poll!")
    except Exception as e:
        print(f"Exception creating poll: {str(e)}")
        import traceback
        traceback.print_exc()

def send_message_with_poll(poll_id):
    url = "https://api.groupme.com/v3/bots/post"
    data = {
        "bot_id": BOT_ID,
        "text": " Runs Poll ",
        "attachments": [
            {
                "type": "poll",
                "poll_id": poll_id
            }
        ]
    }
    
    print(f"Sending message with poll ID: {poll_id}")
    
    try:
        response = requests.post(url, json=data)
        print(f"Message response: {response.status_code}")
        print(f"Message response body: {response.text}")
    except Exception as e:
        print(f"Exception sending message: {str(e)}")

def schedule_polls():
    schedule.every().monday.at("19:30").do(create_poll)
    schedule.every().tuesday.at("19:30").do(create_poll)
    schedule.every().wednesday.at("19:30").do(create_poll)
    schedule.every().thursday.at("19:30").do(create_poll)
    schedule.every().friday.at("18:30").do(create_poll)
    schedule.every().saturday.at("18:30").do(create_poll)
    schedule.every().sunday.at("18:30").do(create_poll)
    
    print("Scheduler started!")
    print(f"Current time: {datetime.now()}")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

@app.route('/', methods=['POST'])
def webhook():
    return "ok", 200

@app.route('/ping', methods=['GET'])
def ping():
    return "Bot is alive!", 200

@app.route('/test-poll', methods=['GET'])
def test_poll():
    create_poll()
    return "Test poll created - check logs!"

if __name__ == '__main__':
    scheduler_thread = Thread(target=schedule_polls, daemon=True)
    scheduler_thread.start()
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
