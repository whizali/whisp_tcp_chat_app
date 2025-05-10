#!/usr/bin/env python3
"""
TCP Chat Application - Client
Computer Networks Course Project

This module implements the client side of a TCP-based chat application.
It connects to the server and allows users to send and receive messages.
"""

import socket
import threading
import sys
import time
from datetime import datetime

# Client configuration
SERVER_HOST = '127.0.0.1'  # The server's hostname or IP address
SERVER_PORT = 5555        # The port used by the server
BUFFER_SIZE = 1024        # Maximum message size

def main():
    """Main function to start the client."""
    print(f"[*] Connecting to TCP Chat Server at {SERVER_HOST}:{SERVER_PORT}")
    
    # TODO: Implement client logic
    
    print("[*] Disconnected from server")

if __name__ == "__main__":
    main()
