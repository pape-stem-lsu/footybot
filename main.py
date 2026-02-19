from flask import Flask, request
import requests
import schedule
import time
from threading import Thread
from datetime import datetime
import os

app = Flask(__name__)

BOT_ID = "4b86ded6c239105623a8a243c6"
GROUP_ID = "103943618"
ACCESS_TOKEN = "dzIrDPvokcfyTAeoj5YA0j5xBR7wY66ySboWso1t"

os.environ['TZ'] = 'America/Chicago'

def create_and_send_poll():
    # Step 1: Create the poll
    poll_url = f"https://api.groupme.com/v3/poll/{GROUP_ID}?token={ACCESS_TOKEN}"
    
    poll_data = {
        "subject": "Are you running today?",
        "options": [
            {"title": "yes"},
            {"title": "no"},
            {"title": "#?"}
        ],
        "type": "single",
        "visibility": "public"
    }
    
    print(f"Creating poll at {datetime.now()}")
    
    try:
        poll_response = requests.post(poll_url, json=poll_data)
        print(f"Poll creation response: {poll_response.status_code}")
        print(f"Poll response body: {poll_response.text}")
        
        if poll_response.status_code in [200, 201]:
            poll_data = poll_response.json()
            
            if 'poll' in poll_data:
                poll_id = poll_data['poll']['id']
                print(f"Poll created with ID: {poll_id}")
                
                # Step 2: Post message with poll to group
                message_url = f"https://api.groupme.com/v3/groups/{GROUP_ID}/messages?token={ACCESS_TOKEN}"
                
                message_data = {
                    "message": {
                        "source_guid": str(datetime.now().timestamp()),
                        "text": "🏃‍♂️ Daily Run Poll 🏃‍♀️",
                        "attachments": [
                            {
                                "type": "poll",
                                "poll_id": poll_id
                            }
                        ]
                    }
                }
                
                message_response = requests.post(message_url, json=message_data)
                print(f"Message response: {message_response.status_code}")
                print(f"Message body: {message_response.text}")
                
                return True
        
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def schedule_polls():
    # Send poll every day at 12:00 PM (noon)
    schedule.every().day.at("12:00").do(create_and_send_poll)
    
    print("Scheduler started!")
    print(f"Current time: {datetime.now()}")
    print("Poll will be sent daily at 12:00 PM Central Time")
    
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
    result = create_and_send_poll()
    if result:
        return "Native poll created successfully!"
    else:
        return "Failed to create poll - check logs"

if __name__ == '__main__':
    scheduler_thread = Thread(target=schedule_polls, daemon=True)
    scheduler_thread.start()
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
