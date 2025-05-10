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

    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"[+] Connected to server at {SERVER_HOST}:{SERVER_PORT}")

        # Main communication loop
        while True:
            # Get user input
            message = input("Enter message (or 'exit' to quit): ")

            # Check if user wants to exit
            if message.lower() == 'exit':
                break

            # Send the message to the server
            client_socket.send(message.encode('utf-8'))
            print(f"[<] Sent: {message}")

            # Receive response from the server
            response = client_socket.recv(BUFFER_SIZE).decode('utf-8')
            print(f"[>] Received: {response}")

    except ConnectionRefusedError:
        print(f"[!] Connection refused. Make sure the server is running at {SERVER_HOST}:{SERVER_PORT}")
    except KeyboardInterrupt:
        print("\n[!] Client interrupted by user")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        # Close the client socket
        if 'client_socket' in locals() and client_socket:
            client_socket.close()
        print("[*] Disconnected from server")

if __name__ == "__main__":
    main()
