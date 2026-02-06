from flask import Flask, request
import requests
import schedule
import time
from threading import Thread
from datetime import datetime
import os

app = Flask(__name__)

BOT_ID = "your_bot_id_here"  # Replace with your actual Bot ID
GROUP_ID = "your_group_id_here"  # We'll need to get this
ACCESS_TOKEN = "your_access_token_here"  # We'll need to get this too

os.environ['TZ'] = 'America/Chicago'

def create_poll():
    url = f"https://api.groupme.com/v3/polls/{GROUP_ID}"
    headers = {
        "X-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    
    poll_data = {
        "subject": "🏃‍♂️ Are you running today?",
        "options": [
            {"title": "yes"},
            {"title": "no"},
            {"title": "#?"}
        ],
        "expiration": 86400,  # 24 hours
        "type": "single"
    }
    
    try:
        response = requests.post(url, json=poll_data, headers=headers)
        if response.status_code == 201:
            poll = response.json()
            # Send message with poll
            send_message_with_poll(poll['poll']['id'])
            print(f"Poll created at {datetime.now()}")
        else:
            print(f"Error creating poll: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def send_message_with_poll(poll_id):
    url = "https://api.groupme.com/v3/bots/post"
    data = {
        "bot_id": BOT_ID,
        "text": "🏃‍♂️ Daily Run Poll 🏃‍♀️",
        "attachments": [
            {
                "type": "poll",
                "poll_id": poll_id
            }
        ]
    }
    requests.post(url, json=data)

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

if __name__ == '__main__':
    scheduler_thread = Thread(target=schedule_polls, daemon=True)
    scheduler_thread.start()
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
