from flask import Flask, request
import requests
import schedule
import time
from threading import Thread
from datetime import datetime
import os

app = Flask(__name__)

BOT_ID = "4b86ded6c239105623a8a243c6"

os.environ['TZ'] = 'America/Chicago'

def send_message(text):
    url = "https://api.groupme.com/v3/bots/post"
    try:
        response = requests.post(url, json={"bot_id": BOT_ID, "text": text})
        print(f"Message sent: {response.status_code}")
        return response.status_code == 202
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def send_poll():
    poll_message = """📊Daily Futsal Runs 

Are you playing today?
React with:
👍 = yes
👎 = no
🤷 = #?
"""
    
    send_message(poll_message)
    print(f"Poll sent at {datetime.now()}")

def schedule_polls():
    schedule.every().monday.at("12:30").do(send_poll)
    schedule.every().tuesday.at("12:30").do(send_poll)
    schedule.every().wednesday.at("12:30").do(send_poll)
    schedule.every().thursday.at("12:30").do(send_poll)
    schedule.every().friday.at("12:30").do(send_poll)
    schedule.every().saturday.at("12:30").do(send_poll)
    schedule.every().sunday.at("12:30").do(send_poll)
    
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
    send_poll()
    return "Test poll sent!"

if __name__ == '__main__':
    scheduler_thread = Thread(target=schedule_polls, daemon=True)
    scheduler_thread.start()
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
