from flask import Flask, request
from pymongo import MongoClient
import datetime

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.github_webhooks

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        # Processing webhook event and saving to MongoDB
        event_type = request.headers.get('X-GitHub-Event')
        if event_type == "push":
            process_push_event(data)
        elif event_type == "pull_request":
            process_pull_request_event(data)
        elif event_type == "merge":
            process_merge_event(data)
        return '', 204

def process_push_event(data):
    author = data['pusher']['name']
    branch = data['ref'].split('/')[-1]
    timestamp = datetime.datetime.utcnow()
    db.events.insert_one({
        "type": "push",
        "author": author,
        "branch": branch,
        "timestamp": timestamp
    })

def process_pull_request_event(data):
    author = data['pull_request']['user']['login']
    from_branch = data['pull_request']['head']['ref']
    to_branch = data['pull_request']['base']['ref']
    timestamp = data['pull_request']['updated_at']
    db.events.insert_one({
        "type": "pull_request",
        "author": author,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": timestamp
    })

def process_merge_event(data):
    author = data['merge_commit']['author']['name']
    from_branch = data['pull_request']['head']['ref']
    to_branch = data['pull_request']['base']['ref']
    timestamp = data['merge_commit']['timestamp']
    db.events.insert_one({
        "type": "merge",
        "author": author,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": timestamp
    })

if __name__ == '__main__':
    app.run(port=5000)
