#!/usr/bin/env python3
"""
Test automatic reconnection with multiple commands over time.
Simulates what happens when gestures trigger actions repeatedly.
"""
import time
from utils.picrawler_connection import PiCrawlerConnect

def test_persistent_reconnection():
    """
    Test socket reconnection by sending status commands over time
    """
    print("\n" + "="*70)
    print("TEST: Persistent Connection with Multiple Commands")
    print("="*70)
    
    pc = PiCrawlerConnect()
    
    # Test 1: Initial connection
    print("\n[TEST 1] Initial Connection")
    print("-" * 70)
    crawler = pc.connection()
    status = pc.getStatus()
    print(f"Connected: {status['connected']}")
    if not pc.is_connected:
        print("FAIL: Could not connect initially")
        return False
    print("PASS: Connected successfully")
    
    # Test 2: Send status immediately
    print("\n[TEST 2] Send Status Command (socket should be fresh)")
    print("-" * 70)
    result1 = pc._send_network_command({"type": "status"})
    print(f"Result: {result1}")
    if not result1.get("success"):
        print("FAIL: First status failed")
        return False
    print("PASS: Status succeeded")
    
    # Test 3: Wait for socket to die (Pi closes after ~1 second)
    print("\n[TEST 3] Wait 2 seconds (Pi closes socket after ~1 sec)")
    print("-" * 70)
    print("Waiting for socket to die on Pi side...")
    time.sleep(2)
    
    # Test 4: Attempt another command (OLD: this would fail, NEW: should reconnect)
    print("\n[TEST 4] Send Status Again (should auto-reconnect)")
    print("-" * 70)
    result2 = pc._send_network_command({"type": "status"})
    print(f"Result: {result2}")
    if not result2.get("success"):
        print("FAIL: Second status failed - no reconnection!")
        return False
    print("PASS: Auto-reconnection succeeded!")
    
    # Test 5: Send another command quickly
    print("\n[TEST 5] Send Another Status (socket still fresh)")
    print("-" * 70)
    result3 = pc._send_network_command({"type": "status"})
    print(f"Result: {result3}")
    if not result3.get("success"):
        print("FAIL: Third status failed")
        return False
    print("PASS: Status succeeded")
    
    # Test 6: Wait again and reconnect
    print("\n[TEST 6] Wait 2 more seconds, then command")
    print("-" * 70)
    print("Waiting again...")
    time.sleep(2)
    result4 = pc._send_network_command({"type": "status"})
    print(f"Result: {result4}")
    if not result4.get("success"):
        print("FAIL: Fourth status failed")
        return False
    print("PASS: Reconnection #2 succeeded!")
    
    # Test 7: Rapid fire commands
    print("\n[TEST 7] Rapid Fire Commands (3x status in quick succession)")
    print("-" * 70)
    for i in range(3):
        result = pc._send_network_command({"type": "status"})
        print(f"Command {i+1}: {result.get('success')}")
        if not result.get("success"):
            print(f"FAIL: Rapid command {i+1} failed")
            return False
    print("PASS: All rapid commands succeeded")
    
    print("\n" + "="*70)
    print("SUCCESS: All reconnection tests passed!")
    print("Socket properly reconnects after server closes connection.")
    print("="*70 + "\n")
    
    pc.close()
    return True

if __name__ == "__main__":
    test_persistent_reconnection()
