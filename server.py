from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

HOSTNAME = os.getenv('HOSTNAME')
SERVER_PORT = int(os.getenv('SERVER_PORT'))

class MyServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        print("GET request received for path:", self.path)
        if self.path == "/":  # Serve the main HTML file
            self.serve_file("templates/index.html", "text/html")
        elif self.path.startswith("/static/"):  # Serve static files
            file_path = self.path.lstrip("/")
            if file_path.endswith(".js"):
                self.serve_file(file_path, "application/javascript")
            elif file_path.endswith(".css"):
                self.serve_file(file_path, "text/css")
            elif file_path.endswith(('.jpg', '.jpeg', '.png', '.gif')):  # Serve image files
                self.serve_file(file_path, "image/jpeg" if file_path.endswith(".jpg") or file_path.endswith(".jpeg") else "image/png" if file_path.endswith(".png") else "image/gif")
            else:
                self.send_error(404, "File not found")
        elif self.path == "/sse":  # Handle SSE
            self.handle_sse()
        else:
            self.send_error(404, "File not found")

    def serve_file(self, file_path, content_type):
        try:
            file_path = os.path.join(os.getcwd(), file_path)  # Ensure absolute path
            with open(file_path, "rb") as file:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_error(404, "File not found")

    def handle_sse(self):
        print("SSE connection established.")
        self.send_response(200)
        self.send_header("Content-type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        try:
            while True:
                # Example: send updates (e.g., JSON list of movement data)
                event_data = json.dumps({"movement": "example_data"})
                self.wfile.write(f"data: {event_data}\n\n".encode('utf-8'))
                self.wfile.flush()
                time.sleep(1)  # Adjust the sleep interval as needed
        except BrokenPipeError:
            print("SSE connection closed by the client.")

    def do_POST(self):
        print("A POST request was sent.")
        content_length = int(self.headers['Content-Length'])
        post_data_bytes = self.rfile.read(content_length)
        post_data_str = post_data_bytes.decode('utf-8')
        print(f"Received POST data: {post_data_str}")

        try:
            data = json.loads(post_data_str)  # Parse JSON data
            print(f"Parsed POST data: {data}")
        except json.JSONDecodeError:
            print("Error decoding JSON")

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))

if __name__ == "__main__":
    webServer = HTTPServer((HOSTNAME, SERVER_PORT), MyServer)
    print(f"Server started http://{HOSTNAME}:{SERVER_PORT}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
