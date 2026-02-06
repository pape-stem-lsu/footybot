from flask import Flask, request
import requests
import schedule
import time
from threading import Thread
from datetime import datetime
import os

app = Flask(__name__)

BOT_ID = "68eb9c29c280ae2cb21829cc8c"

# Set your timezone
os.environ['TZ'] = 'America/Chicago'

# Store votes for the day
votes = {"yes": [], "no": [], "#?": []}

def send_message(text):
    url = "https://api.groupme.com/v3/bots/post"
    try:
        requests.post(url, json={"bot_id": BOT_ID, "text": text})
    except Exception as e:
        print(f"Error sending message: {e}")

def send_poll():
    global votes
    votes = {"yes": [], "no": [], "#?": []}
    
    poll_message = """🏃‍♂️ Daily Run Poll 🏃‍♀️

Are you running today?

Reply with:
✅ yes
❌ no  
❓ #?"""
    
    send_message(poll_message)
    print(f"Poll sent at {datetime.now()}")

def display_results():
    yes_voters = ", ".join(votes["yes"]) if votes["yes"] else "None"
    no_voters = ", ".join(votes["no"]) if votes["no"] else "None"
    maybe_voters = ", ".join(votes["#?"]) if votes["#?"] else "None"
    
    total = len(votes["yes"]) + len(votes["no"]) + len(votes["#?"])
    
    results = f"""📊 Current Results ({total} votes)

✅ YES ({len(votes["yes"])}): {yes_voters}

❌ NO ({len(votes["no"])}): {no_voters}

❓ #? ({len(votes["#?"])}): {maybe_voters}"""
    
    send_message(results)

def schedule_polls():
    # Monday to Thursday at 7:30 PM
    schedule.every().monday.at("19:30").do(send_poll)
    schedule.every().tuesday.at("19:30").do(send_poll)
    schedule.every().wednesday.at("19:30").do(send_poll)
    schedule.every().thursday.at("19:30").do(send_poll)
    
    # Friday to Sunday at 6:30 PM
    schedule.every().friday.at("18:30").do(send_poll)
    schedule.every().saturday.at("18:30").do(send_poll)
    schedule.every().sunday.at("18:30").do(send_poll)
    
    print("Scheduler started!")
    print(f"Current time: {datetime.now()}")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    
    if data.get('sender_type') == 'bot':
        return "ok", 200
    
    message_text = data.get('text', '').lower().strip()
    sender_name = data.get('name', 'Unknown')
    
    if message_text == 'yes':
        votes["no"] = [v for v in votes["no"] if v != sender_name]
        votes["#?"] = [v for v in votes["#?"] if v != sender_name]
        if sender_name not in votes["yes"]:
            votes["yes"].append(sender_name)
        display_results()
    
    elif message_text == 'no':
        votes["yes"] = [v for v in votes["yes"] if v != sender_name]
        votes["#?"] = [v for v in votes["#?"] if v != sender_name]
        if sender_name not in votes["no"]:
            votes["no"].append(sender_name)
        display_results()
    
    elif message_text == '#?' or message_text == '?':
        votes["yes"] = [v for v in votes["yes"] if v != sender_name]
        votes["no"] = [v for v in votes["no"] if v != sender_name]
        if sender_name not in votes["#?"]:
            votes["#?"].append(sender_name)
        display_results()
    
    elif message_text == 'results':
        display_results()
    
    return "ok", 200

@app.route('/ping', methods=['GET'])
def ping():
    return "Bot is alive!", 200
if __name__ == '__main__':
    # Start scheduler in background thread
    scheduler_thread = Thread(target=schedule_polls, daemon=True)
    scheduler_thread.start()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)


