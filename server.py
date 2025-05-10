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

def handle_client(client_socket, client_address):
    """
    Handle communication with a connected client.

    Args:
        client_socket: Socket object for the client connection
        client_address: Tuple containing (ip, port) of the client
    """
    try:
        while True:
            # Receive data from the client
            data = client_socket.recv(BUFFER_SIZE)

            # If no data is received, the client has disconnected
            if not data:
                print(f"[-] Client {client_address[0]}:{client_address[1]} disconnected")
                break

            # Decode the received data
            message = data.decode('utf-8')
            print(f"[>] Received from {client_address[0]}:{client_address[1]}: {message}")

            # Echo the message back to the client
            response = f"Server echo: {message}"
            client_socket.send(response.encode('utf-8'))
            print(f"[<] Sent to {client_address[0]}:{client_address[1]}: {response}")

    except Exception as e:
        print(f"[!] Error handling client {client_address[0]}:{client_address[1]}: {e}")
    finally:
        # Close the client socket
        client_socket.close()
        print(f"[-] Connection with {client_address[0]}:{client_address[1]} closed")

def main():
    """Main function to start the server."""
    print(f"[*] Starting TCP Chat Server on {HOST}:{PORT}")

    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set socket option to reuse address (helps avoid "Address already in use" errors)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # Bind the socket to the address and port
        server_socket.bind((HOST, PORT))

        # Listen for incoming connections (queue up to 5 connection requests)
        server_socket.listen(5)
        print(f"[*] Listening for connections on {HOST}:{PORT}")

        while True:
            # Accept a connection
            client_socket, client_address = server_socket.accept()
            print(f"[+] Accepted connection from {client_address[0]}:{client_address[1]}")

            # Handle client communication
            handle_client(client_socket, client_address)

    except KeyboardInterrupt:
        print("\n[!] Server interrupted by user")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        # Close the server socket
        if server_socket:
            server_socket.close()
        print("[*] Server is shutting down")

if __name__ == "__main__":
    main()
