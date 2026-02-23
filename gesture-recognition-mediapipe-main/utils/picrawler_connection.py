"""
Unified PiCrawler Connection Module
Automatically detects if running on Pi or remotely and uses appropriate method
"""

import json
import time
import socket
import os
import sys
from typing import TYPE_CHECKING

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

        # Detect the environment first, separately from library availability
        self.is_raspberry_pi = self._detect_raspberry_pi()
        self.picrawler_available = False  # ← tracks library separately from hardware detection

        # Only attempt to import picrawler on Raspberry Pi
        if self.is_raspberry_pi:
            try:
                from picrawler import Picrawler
                self.Picrawler = Picrawler
                self.picrawler_available = True
            except ImportError:
                print("⚠ Warning: Running on Raspberry Pi but picrawler library not found.")
                print("  Install it with: pip install picrawler")
                # NOTE: is_raspberry_pi stays True — we ARE on a Pi, just missing the library

    def _detect_raspberry_pi(self) -> bool:
        """
        Robustly detect if code is running on a Raspberry Pi.
        Uses multiple independent checks so no single missing file causes a false negative.
        Returns True only if at least one check confirms Raspberry Pi hardware/OS.
        """

        # Check 1: /proc/cpuinfo — contains hardware model string on real Pi hardware
        try:
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo = f.read()
            if "Raspberry Pi" in cpuinfo or "BCM" in cpuinfo:
                print("[Pi Detection] Confirmed via /proc/cpuinfo")
                return True
        except OSError:
            pass

        # Check 2: /etc/os-release — Raspberry Pi OS identifies itself as 'raspbian' or 'raspberry'
        try:
            with open("/etc/os-release", "r") as f:
                os_release = f.read().lower()
            if "raspbian" in os_release or "raspberry" in os_release:
                print("[Pi Detection] Confirmed via /etc/os-release")
                return True
        except OSError:
            pass

        # Check 3: Device tree model file — most explicit hardware identifier, present on all Pi models
        try:
            with open("/sys/firmware/devicetree/base/model", "r") as f:
                model = f.read().lower()
            if "raspberry pi" in model:
                print("[Pi Detection] Confirmed via device tree model")
                return True
        except OSError:
            pass

        # Check 4: /proc/device-tree/model — alternative path used on some Pi OS versions
        try:
            with open("/proc/device-tree/model", "r") as f:
                model = f.read().lower()
            if "raspberry pi" in model:
                print("[Pi Detection] Confirmed via /proc/device-tree/model")
                return True
        except OSError:
            pass

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
        - Direct: If running on Raspberry Pi with picrawler library available
        - Network: If running on a remote machine (or Pi without the library)
        """
        if self.is_connected:
            return self.get_crawler_object()

        if not self.getDeviceInfo():
            return None

        if self.is_raspberry_pi and self.picrawler_available:
            return self._connect_direct()
        else:
            if self.is_raspberry_pi and not self.picrawler_available:
                print("⚠ On Raspberry Pi but picrawler library unavailable — falling back to network mode.")
            return self._connect_network()

    def _connect_direct(self):
        """Direct connection for Raspberry Pi"""
        try:
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
                self.socket.settimeout(5)
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
            print("✗ Connection refused: PiCrawler server not running on Pi")
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
            self.socket.sendall(command_json.encode("utf-8"))
            response = self.socket.recv(1024).decode("utf-8")
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
                if action_name in crawler.move_list:
                    crawler.do(crawler.move_list[action_name])
                    print(f"✓ Action executed: {action_name}")
                    return True
                else:
                    print(f"✗ Unknown action: {action_name}")
                    return False

            elif self.connection_type == "network":
                command = {"type": "action", "action": action_name}
                response = self._send_network_command(command)
                if response and response.get("success"):
                    print(f"✓ Action executed: {action_name}")
                    return True

            return False
        except Exception as e:
            print(f"✗ Cannot execute action: {e}")
            return False

    def stand(self):        return self.executeAction("stand")
    def sit(self):          return self.executeAction("sit")
    def wave(self):         return self.executeAction("wave_hand")
    def nod(self):          return self.executeAction("nod")
    def shake_head(self):   return self.executeAction("shake_head")
    def excited(self):      return self.executeAction("excited")
    def fighting(self):     return self.executeAction("fighting")
    def play_dead(self):    return self.executeAction("play_dead")
    def shake_hand(self):   return self.executeAction("shake_hand")
    def look_left(self):    return self.executeAction("look_left")
    def look_right(self):   return self.executeAction("look_right")
    def look_up(self):      return self.executeAction("look_up")
    def look_down(self):    return self.executeAction("look_down")
    def warm_up(self):      return self.executeAction("warm_up")
    def push_up(self):      return self.executeAction("push_up")

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
                command = {"type": "move", "leg": leg_index, "coords": [x, y, z]}
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
                print("✓ All legs moved")
                return True

            elif self.connection_type == "network":
                command = {"type": "move_all", "coords": coords}
                response = self._send_network_command(command)
                if response and response.get("success"):
                    print("✓ All legs moved")
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
        print(f"Connection Type:      {status['connection_type']}")
        print(f"Is Raspberry Pi:      {status['is_raspberry_pi']}")
        print(f"PiCrawler Available:  {status['picrawler_available']}")

    def getStatus(self):
        """Get connection status"""
        return {
            "connected": self.is_connected,
            "connection_type": self.connection_type,
            "is_raspberry_pi": self.is_raspberry_pi,        # hardware/OS detection
            "picrawler_available": self.picrawler_available, # library detection (separate!)
            "config_loaded": bool(self.config),
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