from flask import Flask, send_from_directory, jsonify, request, render_template, Response
import os
import json
import time
from dotenv import load_dotenv

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
        # Add this client to the list of connected clients
        clients.append(request)

        try:
            while True:
                data = load_json_data()  # Read from Helpys.json file
                event_data = json.dumps(data)
                yield f"data: {event_data}\n\n"
                time.sleep(1)  # Simulate sending updates every second
        except GeneratorExit:
            # Remove the client when it disconnects
            print("SSE client disconnected.")
            clients.remove(request)

    return Response(generate(), content_type='text/event-stream', status=200)


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

        data = load_json_data()  # Load the current data from Helpys.json
        data.update(content)  # Assuming the content is a dictionary with keys to update

        save_json_data(data)  # Save the updated data back to Helpys.json

        return jsonify({'status': 'success', 'message': 'JSON updated'}), 200
    else:
        print("Invalid data received.")
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400



if __name__ == "__main__":
    app.run(host=HOSTNAME, port=SERVER_PORT, debug=True)
