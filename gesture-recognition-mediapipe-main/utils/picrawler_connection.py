"""
Unified PiCrawler Connection Module
Automatically detects if running on Pi or remotely and uses appropriate method
"""

import json
import time
import socket
import os
import sys

class PiCrawlerConnect:
    """
    Smart connection handler that works both locally (on Pi) and remotely (over network)
    """
    
    def __init__(self, config_path="data/GestureSettings.json"):
        self.config_path = config_path
        self.config = {}
        self.crawler = None
        self.socket = None
        self.is_connected = False
        self.connection_type = None
        self.is_raspberry_pi = self._detect_raspberry_pi()
        
        # Only import picrawler on Raspberry Pi
        if self.is_raspberry_pi:
            try:
                from picrawler import Picrawler
                self.Picrawler = Picrawler
            except ImportError:
                print("⚠ Warning: picrawler library not found on Raspberry Pi")
                self.is_raspberry_pi = False
    
    def _detect_raspberry_pi(self):
        """Check if code is running on Raspberry Pi"""
        try:
            # Check for Raspberry Pi specific files/info
            with open('/etc/os-release') as f:
                content = f.read().lower()
                return 'raspbian' in content or 'raspberry' in content
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    def getDeviceInfo(self):
        """Load configuration from JSON"""
        try:
            with open(self.config_path) as jsonfile:
                settings = json.load(jsonfile)
                self.config = settings.get("picrawler_info", {})
                return True
        except FileNotFoundError:
            print(f"✗ Config file not found: {self.config_path}")
            return False
        except json.JSONDecodeError:
            print(f"✗ Invalid JSON in config file: {self.config_path}")
            return False
    
    def connection(self):
        """
        Establish connection using appropriate method:
        - Direct: If running on Raspberry Pi
        - Network: If running on remote machine
        """
        if self.is_connected:
            return self.get_crawler_object()
        
        if not self.getDeviceInfo():
            return None
        
        # Try to connect using detected method
        if self.is_raspberry_pi:
            return self._connect_direct()
        else:
            return self._connect_network()
    
    def _connect_direct(self):
        """Direct connection for Raspberry Pi"""
        try:
            if not hasattr(self, 'Picrawler'):
                print("✗ PiCrawler library not available on this Raspberry Pi")
                return None
            
            if self.crawler is None:
                init_angles = self.config.get("init_angles", None)
                self.crawler = self.Picrawler(init_angles=init_angles)
                time.sleep(0.5)
            
            self.is_connected = True
            self.connection_type = "direct"
            print("✓ Connected to PiCrawler (Direct/Local)")
            return self.crawler
        
        except Exception as e:
            print(f"✗ Failed to connect directly: {e}")
            return None
    
    def _connect_network(self):
        """Network connection for remote machines"""
        try:
            if self.socket is None:
                robot_ip = self.config.get("ip_address")
                robot_port = self.config.get("port", 5005)
                
                if not robot_ip:
                    print("✗ Error: 'ip_address' not set in config")
                    print("  Please add your Raspberry Pi IP address to data/GestureSettings.json")
                    print("  Example: '192.168.1.100'")
                    return None
                
                print(f"🔗 Connecting to PiCrawler at {robot_ip}:{robot_port}...")
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(5)  # 5 second timeout
                self.socket.connect((robot_ip, robot_port))
            
            self.is_connected = True
            self.connection_type = "network"
            print(f"✓ Connected to PiCrawler (Network: {self.config.get('ip_address')})")
            return self
        
        except socket.timeout:
            print(f"✗ Connection timeout: Cannot reach PiCrawler at {self.config.get('ip_address')}:{self.config.get('port', 5005)}")
            print("  Make sure:")
            print("  1. The Raspberry Pi is powered on and connected to WiFi")
            print("  2. The IP address in config is correct")
            print("  3. picrawler_server.py is running on the Pi")
            return None
        except ConnectionRefusedError:
            print(f"✗ Connection refused: PiCrawler server not running on Pi")
            print("  Run this on the Raspberry Pi: sudo python3 picrawler_server.py")
            return None
        except Exception as e:
            print(f"✗ Failed to connect over network: {e}")
            return None
    
    def get_crawler_object(self):
        """Get the appropriate crawler object"""
        if self.connection_type == "direct":
            return self.crawler
        elif self.connection_type == "network":
            return self
        return None
    
    def _send_network_command(self, command_dict):
        """Send command over network"""
        try:
            command_json = json.dumps(command_dict)
            self.socket.sendall(command_json.encode('utf-8'))
            response = self.socket.recv(1024).decode('utf-8')
            return json.loads(response)
        except Exception as e:
            print(f"✗ Network error: {e}")
            self.is_connected = False
            self.socket = None
            return {"success": False}
    
    # ==================== ACTION METHODS ====================
    
    def executeAction(self, action_name):
        """Execute a predefined action"""
        try:
            crawler = self.connection()
            if not crawler:
                return False
            
            if self.connection_type == "direct":
                # Direct connection on Pi
                if action_name in crawler.move_list:
                    crawler.do(crawler.move_list[action_name])
                    print(f"✓ Action executed: {action_name}")
                    return True
                else:
                    print(f"✗ Unknown action: {action_name}")
                    return False
            
            elif self.connection_type == "network":
                # Network connection
                command = {
                    "type": "action",
                    "action": action_name
                }
                response = self._send_network_command(command)
                if response and response.get("success"):
                    print(f"✓ Action executed: {action_name}")
                    return True
            
            return False
        except Exception as e:
            print(f"✗ Cannot execute action: {e}")
            return False
    
    def stand(self):
        return self.executeAction("stand")
    
    def sit(self):
        return self.executeAction("sit")
    
    def wave(self):
        return self.executeAction("wave_hand")
    
    def nod(self):
        return self.executeAction("nod")
    
    def shake_head(self):
        return self.executeAction("shake_head")
    
    def excited(self):
        return self.executeAction("excited")
    
    def fighting(self):
        return self.executeAction("fighting")
    
    def play_dead(self):
        return self.executeAction("play_dead")
    
    def shake_hand(self):
        return self.executeAction("shake_hand")
    
    def look_left(self):
        return self.executeAction("look_left")
    
    def look_right(self):
        return self.executeAction("look_right")
    
    def look_up(self):
        return self.executeAction("look_up")
    
    def look_down(self):
        return self.executeAction("look_down")
    
    def warm_up(self):
        return self.executeAction("warm_up")
    
    def push_up(self):
        return self.executeAction("push_up")
    
    # ==================== MOVEMENT METHODS ====================
    
    def moveToCoordinates(self, leg_index, x, y, z):
        """Move a specific leg to coordinates"""
        try:
            crawler = self.connection()
            if not crawler:
                return False
            
            if self.connection_type == "direct":
                crawler.move(leg_index, [x, y, z])
                print(f"✓ Leg {leg_index} moved to [{x}, {y}, {z}]")
                return True
            
            elif self.connection_type == "network":
                command = {
                    "type": "move",
                    "leg": leg_index,
                    "coords": [x, y, z]
                }
                response = self._send_network_command(command)
                if response and response.get("success"):
                    print(f"✓ Leg {leg_index} moved to [{x}, {y}, {z}]")
                    return True
            
            return False
        except Exception as e:
            print(f"✗ Cannot move leg: {e}")
            return False
    
    def setAllLegsCoordinates(self, coords):
        """Set coordinates for all 4 legs"""
        try:
            crawler = self.connection()
            if not crawler:
                return False
            
            if self.connection_type == "direct":
                crawler.move(coords)
                print(f"✓ All legs moved")
                return True
            
            elif self.connection_type == "network":
                command = {
                    "type": "move_all",
                    "coords": coords
                }
                response = self._send_network_command(command)
                if response and response.get("success"):
                    print(f"✓ All legs moved")
                    return True
            
            return False
        except Exception as e:
            print(f"✗ Cannot move legs: {e}")
            return False
    
    # ==================== UTILITY METHODS ====================
    
    def listAvailableActions(self):
        """List all available actions"""
        actions = [
            "sit", "stand", "wave_hand", "shake_hand", "fighting",
            "excited", "play_dead", "nod", "shake_head", "look_left",
            "look_right", "look_up", "look_down", "warm_up", "push_up"
        ]
        print("\n=== Available Actions ===")
        for i, action in enumerate(actions, 1):
            print(f"{i:2d}. {action}")
        print("=" * 30)
        status = self.getStatus()
        print(f"Connection Type: {status['connection_type']}")
        print(f"Is Raspberry Pi: {status['is_raspberry_pi']}")
    
    def getStatus(self):
        """Get connection status"""
        return {
            "connected": self.is_connected,
            "connection_type": self.connection_type,
            "is_raspberry_pi": self.is_raspberry_pi,
            "config_loaded": bool(self.config)
        }
    
    def close(self):
        """Close connection gracefully"""
        try:
            self.sit()
            time.sleep(0.5)
            
            if self.connection_type == "network" and self.socket:
                self.socket.close()
            
            self.crawler = None
            self.socket = None
            self.is_connected = False
            print("✓ PiCrawler connection closed")
        except Exception as e:
            print(f"⚠ Error closing connection: {e}")