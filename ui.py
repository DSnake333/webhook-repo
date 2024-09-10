from flask import Flask, render_template, jsonify
import pymongo

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.github_webhooks

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events')
def get_events():
    events = list(db.events.find().sort("timestamp", -1).limit(10))
    return jsonify(events)

if __name__ == '__main__':
    app.run(port=5000)
