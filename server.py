from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import json

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    movementlist = []
    def do_GET(self):
        if self.path == "/":  # Serve the main HTML file
            self.serve_file("templates/index.html", "text/html")
        elif self.path.startswith("/static/"):  # Serve static files
            file_path = self.path.lstrip("/")
            if file_path.endswith(".js"):
                self.serve_file(file_path, "application/javascript")
            elif file_path.endswith(".css"):
                self.serve_file(file_path, "text/css")
            else:
                self.send_error(404, "File not found")
        else:
            self.send_error(404, "File not found")

    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, "rb") as file:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_error(404, "File not found")

    def do_POST(self):

        print("A POST request was sent.")
        content_length = int(self.headers['Content-Length'])
        post_data_bytes = self.rfile.read(content_length)
        print(f"Received POST data: {post_data_bytes.decode('utf-8')}")

        data = json.loads(post_data_bytes.decode('utf-8'))

        if data.get("type") == "command":
            command = data.get("command")
            self.movementlist.append(command)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"{'status': 'success'}")

        if data.get("type") == "turtlecheck":
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(self.movementlist).encode('utf-8'))

            self.movementlist.clear()

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print(f"Server started http://{hostName}:{serverPort}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
