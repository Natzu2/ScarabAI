"""
Copy

import socket
import json
import time
from picrawler import Picrawler
from threading import Thread
 
 
class PicrawlerServer:
    # A server running on Raspberry Pi that accepts commands from networked clients.
    # Run on Pi: sudo python3 picrawler_server.py
    
 
    def __init__(self, port=5005):
        self.port = port
        self.crawler = None
        self.is_running = False
 
    def initialize_crawler(self):
        # Initialize the Picrawler instance.
        # Returns True if successful, False otherwise.
        
        try:
            self.crawler = Picrawler()
            time.sleep(1)
            print("Picrawler initialized successfully.")
            print(f"Available actions: {list(self.crawler.move_list.keys())}")
            return True
        except Exception as e:
            print(f"Failed to initialize Picrawler: {e}")
            return False
 
    def _recv_message(self, client_socket):
        # Read a complete newline-delimited JSON message from the socket.

        buffer = ""
        while True:
            chunk = client_socket.recv(1024).decode("utf-8")
            if not chunk:
                return None  # client closed the connection
            buffer += chunk
            if "\n" in buffer:
                message, _ = buffer.split("\n", 1)
                return json.loads(message)
 
    def handle_client(self, client_socket, address):
        # Handle an individual client connection in its own thread.
        print(f"Client connected from {address}")
        try:
            while True:
                command = self._recv_message(client_socket)
                if command is None:
                    break
                response = self.process_command(command)
                client_socket.send((json.dumps(response) + "\n").encode("utf-8"))
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            print(f"Client {address} disconnected.")
 
    def process_command(self, command):
        # Process a received command and execute the corresponding action.
 
        try:
            cmd_type = command.get("type")
 
            if cmd_type == "action":
                action = command.get("action")
 
                # Validate that the action exists in move_list
                try:
                    action_steps = self.crawler.move_list[action]
                except Exception:
                    print(f"[Action rejected] '{action}' not found in move_list.")
                    return {"status": "error", "message": f"Unknown action: {action}"}
 
                print(f"[Action received] '{action}' — dispatching...")
 
                def run_action(steps):
                    try:
                        for step in steps:
                            self.crawler.do_step(step, speed=80)
                    except Exception as e:
                        print(f"[Action error] '{action}' failed mid-execution: {e}")
 
                action_thread = Thread(target=run_action, args=(action_steps,), daemon=True)
                action_thread.start()
 
                print(f"[Action dispatched] '{action}' running in background thread.")
                return {"status": "success", "message": f"Executing action: {action}"}
 
            elif cmd_type == "status":
                return {"status": "success", "message": "Picrawler server is running."}
 
            else:
                print(f"[Command rejected] Unknown command type: '{cmd_type}'")
                return {"status": "error", "message": f"Unknown command type: {cmd_type}"}
 
        except Exception as e:
            print(f"[process_command error] {e}")
            return {"status": "error", "message": f"Server error: {e}"}
 
    def start_server(self):
        # Start the TCP server and listen for incoming client connections.
        if not self.initialize_crawler():
            return
 
        self.is_running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", self.port))
        server_socket.listen(5)
 
        print(f"Picrawler server listening on port {self.port}...")
 
        try:
            while self.is_running:
                client_socket, address = server_socket.accept()
                client_thread = Thread(
                    target=self.handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
        except KeyboardInterrupt:
            print("Shutting down server...")
        finally:
            server_socket.close()
            self.is_running = False
            print("Server stopped.")
 
 
if __name__ == "__main__":
    server = PicrawlerServer(port=5005)
    server.start_server()
    """