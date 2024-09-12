from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)

client = MongoClient(
    'mongodb+srv://dharshak3:OrKoyqjOxHJdmGW0@cluster0.gzqct.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.github_webhooks

# Store the last fetched timestamp globally for simplicity
last_fetched_time = datetime.utcnow() - timedelta(seconds=15)  # Start with the last 15 seconds


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        print("Received webhook event:", data)
        event_type = request.headers.get('X-GitHub-Event')

        if event_type == "push":
            process_push_event(data)
        elif event_type == "pull_request":
            process_pull_request_event(data)

        return '', 204


def process_push_event(data):
    author = data['pusher']['name']
    branch = data['ref'].split('/')[-1]
    timestamp = datetime.utcnow()

    timestamp_seconds = timestamp.replace(microsecond=0)

    head_commit = data.get('head_commit', {})
    parent_count = len(head_commit.get('parents', []))

    if parent_count <= 1:
        recent_merge_time = (timestamp_seconds - timedelta(seconds=3)).isoformat() + 'Z'

        print(f"Looking for recent merge events on branch {branch} after {recent_merge_time}")

        recent_merge = db.events.find_one({
            "type": "merge",
            "to_branch": branch,
            "timestamp": {"$gte": recent_merge_time}
        })

        if recent_merge:
            print(f"Skipping push event because a recent merge was found: {recent_merge}")
        else:
            print(f"Inserting push event for branch {branch} at {timestamp_seconds.isoformat() + 'Z'}")
            db.events.insert_one({
                "type": "push",
                "author": author,
                "branch": branch,
                "timestamp": timestamp_seconds.isoformat() + 'Z'
            })


def process_pull_request_event(data):
    author = data['pull_request']['user']['login']
    from_branch = data['pull_request']['head']['ref']
    to_branch = data['pull_request']['base']['ref']
    timestamp = data['pull_request']['updated_at']
    merged = data['pull_request']['merged']

    if isinstance(timestamp, str):
        timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").isoformat() + 'Z'

    if merged:
        db.events.insert_one({
            "type": "merge",
            "author": author,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        })
    else:
        db.events.insert_one({
            "type": "pull_request",
            "author": author,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        })


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/events', methods=['GET'])
def get_events():
    # Check if this is the initial load
    is_initial_load = request.args.get('initial', 'false') == 'true'

    if is_initial_load:
        # Fetch all events (no time limit)
        events = list(db.events.find().sort("timestamp", -1))  # Fetch all events
    else:
        # For subsequent fetches, only get the last 15 seconds of events
        time_window = datetime.utcnow() - timedelta(seconds=15)
        events = list(
            db.events.find({"timestamp": {"$gte": time_window.isoformat() + 'Z'}}).sort("timestamp", -1)
        )

    # Prepare events for JSON response
    for event in events:
        event['_id'] = str(event['_id'])
        event['author'] = event.get('author', 'Unknown')
        event['type'] = event.get('type', 'Unknown')
        event['branch'] = event.get('branch', 'Unknown')
        event['from_branch'] = event.get('from_branch', 'Unknown')
        event['to_branch'] = event.get('to_branch', 'Unknown')
        event['timestamp'] = event.get('timestamp', 'Unknown')

    return jsonify(events)


if __name__ == '__main__':
    app.run(port=5000)
