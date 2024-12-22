from flask import Flask, send_from_directory, jsonify, request, render_template, Response
import os
import json
import time
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

load_dotenv()

HOSTNAME = os.getenv('HOSTNAME')
SERVER_PORT = int(os.getenv('SERVER_PORT'))

app = Flask(__name__)

HELPYS_JSON_PATH = 'Helpys.json'  # Path to the JSON file

# In-memory list to track clients connected via SSE
clients = []

def load_json_data():
    """Load data from the Helpys.json file."""
    try:
        with open(HELPYS_JSON_PATH, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {HELPYS_JSON_PATH}")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {HELPYS_JSON_PATH}")
        return {}

def save_json_data(data):
    """Save updated data to Helpys.json."""
    try:
        with open(HELPYS_JSON_PATH, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving JSON data: {e}")

def cleanup_old_entries():
    """Remove entries older than 30 days from Helpys.json."""
    print("Running JSON cleanup...")
    data = load_json_data()
    if not data:
        print("No data to clean.")
        return

    # Get the current date
    current_date = datetime.datetime.now()

    # Iterate over the entries and remove those older than 30 days
    keys_to_remove = []
    for key, value in data.items():
        try:
            last_seen_date = datetime.datetime.strptime(value['LastSeen'], "%d/%m/%Y")
            if (current_date - last_seen_date).days > 30:
                keys_to_remove.append(key)
        except (KeyError, ValueError):
            print(f"Invalid or missing LastSeen date for {key}.")

    for key in keys_to_remove:
        print(f"Removing outdated entry: {key}")
        del data[key]

    save_json_data(data)

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_old_entries, 'interval', days=1)
scheduler.start()
cleanup_old_entries()

@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("Scheduler shut down gracefully.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    file_extension = filename.split('.')[-1].lower()
    content_type = {
        'js': 'application/javascript',
        'css': 'text/css',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif'
    }.get(file_extension, 'application/octet-stream')

    try:
        return send_from_directory(os.getcwd(), filename, mimetype=content_type)
    except FileNotFoundError:
        return "File not found", 404

@app.route('/sse')
def sse():
    def generate():
        print("SSE connection established.")
        
        # Create a response object for this client
        def event_stream():
            while True:
                data = load_json_data()  # Read from Helpys.json file
                event_data = json.dumps(data)
                yield f"data: {event_data}\n\n"
                time.sleep(1)  # Simulate sending updates every second

        # Add this generator to the list of connected clients
        clients.append(event_stream)

        try:
            return Response(event_stream(), content_type='text/event-stream')
        except GeneratorExit:
            print("SSE client disconnected.")
            clients.remove(event_stream)

    return generate()

@app.route('/get_json')
def get_json():
    data = load_json_data()  # Load data from Helpys.json file
    return jsonify(data)


@app.route('/update_json', methods=['POST'])
def update_json():
    print("Received POST data to update JSON.")
    content = request.get_json()  # Get JSON data from the request

    if content:
        print(f"Content received: {content}")  # This will show what was received

         # Add "LastSeen" to each section in the content
        for key in content:
            if isinstance(content[key], dict):  # Ensure the section is a dictionary
                content[key]["LastSeen"] = datetime.datetime.now().strftime("%d/%m/%Y")

        print(f"Content updated: {content}")

        data = load_json_data()  # Load the current data from Helpys.json
        data.update(content)  # Assuming the content is a dictionary with keys to update
        
        save_json_data(data)  # Save the updated data back to Helpys.json

        return jsonify({'status': 'success', 'message': 'JSON updated'}), 200
    else:
        print("Invalid data received.")
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

if __name__ == "__main__":
    app.run(host=HOSTNAME, port=SERVER_PORT, debug=True)
