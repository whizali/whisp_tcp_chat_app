#!/usr/bin/env python3
"""
TCP Chat Application - Server
Computer Networks Course Project

This module implements the server side of a TCP-based chat application.
It handles multiple client connections and broadcasts messages between clients.
"""

import socket
import threading
import select
import sys
import time
from datetime import datetime

# Server configuration
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 5555        # Port to listen on (non-privileged ports are > 1023)
BUFFER_SIZE = 1024  # Maximum message size

def main():
    """Main function to start the server."""
    print(f"[*] Starting TCP Chat Server on {HOST}:{PORT}")
    
    # TODO: Implement server logic
    
    print("[*] Server is shutting down")

if __name__ == "__main__":
    main()
