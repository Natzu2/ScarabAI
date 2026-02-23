import socket
import json
import time

class PiCrawlerConnect:
    """
    Network connection handler for PiCrawler device over wifi/Bluetooth
    Runs on the main pc.
    """

    def __init__(self, config_path= "data/GestureSettings.json"):
        self.config_path = config_path
        self.config = {}
        self.is_connected = False
        self.socket = None
        self.robot_ip = None
        self.robot_port = None

    def getDeviceInfo(self):
        """
        Load PiCrawler network configuration from a JSON file.
        """
        try:
            with open(self.config_path) as jsonfile:
                settings = json.load(jsonfile)
                crawler_settings = settings.get("crawler_info", {})
                self.robot_ip = crawler_settings.get("ip_address")
                self.robot_port = crawler_settings.get("port", 5005)  # Default port
                return True
        except FileNotFoundError:
            print(f"Config file not found: {self.config_path}")
            return False
        
    def connection(self):
        """
        Establish a network connection to the PiCrawler on Rapsberry Pi.
        """
        try:
            if not self.is_connected:
                self.getDeviceInfo()
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.robot_ip, self.robot_port))
                self.is_connected = True
                print(f"Connected to PiCrawler at {self.robot_ip}:{self.robot_port}.")
            return self.socket
        except Exception as e:
            print(f"Failed to connect to PiCrawler: {e}")
            self.is_connected = False
            return None
        
    def sendCommand(self, command_dict):
        """
        Send a command to the PiCrawler device as a JSON string.
        
        :param command_dict: A dictionary containing the command details.
        """
        try:
            sock = self.connection()
            if not sock:
                return False
            
            command_json = json.dumps(command_dict)
            sock.sendall(command_json.encode('utf-8'))

            response = sock.recv(1024).decode('utf-8')
            return json.loads(response)
        except Exception as e:
            print(f"Error sending command to PiCrawler: {e}")
            return None
        
        