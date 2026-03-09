"""import socket
import json
import time
from picrawler import Picrawler
from threading import Thread

class PicrawlerServer:
    ""A server running on Rapsberry Pi that accepts command from the networked clients.
        Install on Pi: sudo python 3 picrawler_server.py
    ""

    def __init__(self, port=5005):
        self.port = port
        self.crawler = None
        self.is_running = False


    def initialize_crawler(self):
        ""Initialize the Picrawler instance.
            Returns True if initialization is successful, False otherwise.
            ""
        try:
            self.crawler = Picrawler()
            time.sleep(1)  # Allow time for the crawler to initialize
            print("Picrawler initialized.")
            return True
        except Exception as e:
            print(f"Failed to initialize Picrawler: {e}")
            return False

    def _recv_message(self, client_socket):
        ""
        Read a complete newline-delimited JSON message from the socket.

        TCP does not guarantee that one send() arrives as one recv(), so a
        raw recv(1024) can return a partial JSON string and crash json.loads().
        Both client and server now terminate every message with '\\n', and this
        method accumulates chunks until the delimiter is found before parsing.

        Returns the parsed dict, or None if the connection closed cleanly.
        Raises an exception on socket errors or malformed JSON.
        ""
        buffer = ""
        while True:
            chunk = client_socket.recv(1024).decode("utf-8")
            if not chunk:
                return None          # client closed the connection
            buffer += chunk
            if "\n" in buffer:
                message, _ = buffer.split("\n", 1)
                return json.loads(message)

    def handle_client(self, client_socket, address):
        ""Handle incoming client connections and commands.
            Receives commands from the client, processes them, and sends back responses.""

        print(f"Client connected from {address}")

        try:
            while True:
                # Receive a complete newline-delimited command from the client
                command = self._recv_message(client_socket)
                if command is None:
                    break

                response = self.process_command(command)
                # Terminate response with newline so the client can frame it correctly
                client_socket.send((json.dumps(response) + "\n").encode("utf-8"))
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            print(f"Client {address} disconnected.")

    def process_command(self, command):
        ""Process the received command and execute corresponding actions on the Picrawler.
         The command should be a dictionary with a "type" key indicating the command type (e.g., "action", "move", "status").
         Returns a response dictionary indicating the result of the command execution.

         Action commands are dispatched in a background thread so that crawler.do()
         (which blocks for the full animation duration) does not stall the socket loop.
         The server responds immediately with {"status": "success"} and the action
         runs concurrently — this keeps the connection alive between rapid commands.
         ""
        try:
            cmd_type = command.get("type")

            if cmd_type == "action":
                action = command.get("action")
                if action in self.crawler.move_list:
                    # Run the animation in a daemon thread so the socket loop
                    # is never blocked while the robot is physically moving.
                    action_thread = Thread(
                        target=self.crawler.do,
                        args=(self.crawler.move_list[action],),
                        daemon=True
                    )
                    action_thread.start()
                    return {"status": "success", "message": f"Executed action: {action}"}
                else:
                    return {"status": "error", "message": f"Unknown action: {action}"}

            elif cmd_type == "move":
                leg = command.get("leg")
                coords = command.get("coords")
                self.crawler.move(leg, coords)
                return {"status": "success", "message": f"Moved leg {leg} to {coords}"}

            elif cmd_type == "status":
                return {"success": True, "status": "Picrawler is running."}

            else:
                return {"success": False, "message": "Unknown command type."}

        except Exception as e:
            return {"success": False, "message": f"Error processing command: {e}"}


    def start_server(self):
        ""Start the server to listen for incoming client connections.
            Initializes the Picrawler and sets up a socket server to handle client connections in separate threads.""

        if not self.initialize_crawler():
            return

        self.is_running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', self.port))
        server_socket.listen(5)

        print(f"Picrawler server started on port {self.port}. Waiting for clients...")

        try:
            while self.is_running:
                client_socket, address = server_socket.accept()
                #Handles each client connection in a separate thread
                client_thread = Thread(target=self.handle_client, args=(client_socket, address))
                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            print("Shutting down server...")
        finally:
            server_socket.close()
            self.is_running = False

if __name__ == "__main__":
    server = PicrawlerServer(port=5005)
    server.start_server()
    """