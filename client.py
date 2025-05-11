#!/usr/bin/env python3
"""
TCP Chat Application - Client
Computer Networks Course Project

This module implements the client side of a TCP-based chat application.
It connects to the server and supports username registration, commands, and private messaging.
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

# Global variables
running = True  # Flag to control the receive thread
username = None  # The client's username

# Available commands (for local help)
COMMANDS = {
    '/help': 'Show available commands',
    '/list': 'List all connected users',
    '/whisper': 'Send a private message to a user: /whisper <username> <message>',
    '/exit': 'Disconnect from the server',
    '/nick': 'Change your username: /nick <new_username> (you are assigned a default username when you connect)'
}

def get_timestamp():
    """Get a formatted timestamp for messages."""
    return datetime.now().strftime('[%H:%M:%S]')

def display_help():
    """Display help information about available commands."""
    print("\n--- Available Commands ---")
    for cmd, desc in COMMANDS.items():
        print(f"  {cmd} - {desc}")
    print("-------------------------")

def receive_messages(client_socket):
    """
    Function to continuously receive messages from the server.

    Args:
        client_socket: Socket connected to the server
    """
    global running, username

    try:
        while running:
            try:
                # Receive data from the server
                data = client_socket.recv(BUFFER_SIZE)

                # If no data is received, the server has disconnected
                if not data:
                    print("\n[!] Server disconnected")
                    running = False
                    break

                # Decode and print the received message
                message = data.decode('utf-8')

                # Check if this is the default username assignment message
                if "You have been assigned the username '" in message and username is None:
                    # Extract the default username from the message
                    start_index = message.find("You have been assigned the username '") + len("You have been assigned the username '")
                    end_index = message.find("'.", start_index)
                    if start_index > 0 and end_index > start_index:
                        username = message[start_index:end_index]
                        print(f"\n{message}")
                        print(f"{get_timestamp()} [CLIENT] Default username set to '{username}'")
                    else:
                        print(f"\n{message}")
                # Check if this is a successful username change confirmation
                elif "Your username has been changed to '" in message:
                    # Extract the new username from the message
                    start_index = message.find("Your username has been changed to '") + len("Your username has been changed to '")
                    end_index = message.find("'.", start_index)
                    if start_index > 0 and end_index > start_index:
                        username = message[start_index:end_index]
                        print(f"\n{message}")
                        print(f"{get_timestamp()} [CLIENT] Username successfully changed to '{username}'")
                    else:
                        print(f"\n{message}")
                # Check if this is a username already taken message
                elif "Username '" in message and "' is already taken" in message:
                    print(f"\n{message}")
                    print(f"{get_timestamp()} [CLIENT] Username change failed - already taken")
                else:
                    # Print the message with a newline to avoid overwriting the input prompt
                    print(f"\n{message}")

                # Reprint the input prompt
                print("Enter message (or '/help' for commands): ", end='', flush=True)

            except ConnectionResetError:
                print("\n[!] Connection reset by server")
                running = False
                break

    except Exception as e:
        print(f"\n[!] Error receiving messages: {e}")
        running = False

def main():
    """Main function to start the client."""
    global running, username

    print(f"[*] Connecting to TCP Chat Server at {SERVER_HOST}:{SERVER_PORT}")

    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set a timeout for connection attempts
        client_socket.settimeout(10)

        # Connect to the server
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"[+] Connected to server at {SERVER_HOST}:{SERVER_PORT}")

        # Reset the timeout to None (blocking mode) for normal operation
        client_socket.settimeout(None)

        # Create and start a thread for receiving messages
        receive_thread = threading.Thread(
            target=receive_messages,
            args=(client_socket,),
            daemon=True  # Daemon threads exit when the main thread exits
        )
        receive_thread.start()

        # Main communication loop for sending messages
        while running:
            # Get user input
            message = input("Enter message (or '/help' for commands): ")

            # Check for local command handling
            if message.lower() == '/help':
                # Display help locally
                display_help()
                # Also send to server for its help
                client_socket.send(message.encode('utf-8'))
                continue

            # Check if user wants to exit
            if message.lower() == '/exit':
                # Send exit command to server
                client_socket.send(message.encode('utf-8'))
                print(f"{get_timestamp()} [CLIENT] Disconnecting...")
                running = False
                break

            # Send the message to the server
            client_socket.send(message.encode('utf-8'))

            # For /nick commands, we'll let the server response handler update the username
            # The username will only be updated when the server confirms the change
            if message.startswith('/nick '):
                parts = message.split(' ', 1)
                if len(parts) > 1:
                    # Store the requested username temporarily, but don't update yet
                    requested_username = parts[1]
                    print(f"{get_timestamp()} [CLIENT] Requesting username change to '{requested_username}'...")

    except ConnectionRefusedError:
        print(f"[!] Connection refused. Make sure the server is running at {SERVER_HOST}:{SERVER_PORT}")
    except socket.timeout:
        print(f"[!] Connection attempt timed out. Server might be busy or unreachable.")
    except KeyboardInterrupt:
        print("\n[!] Client interrupted by user")
        running = False
    except Exception as e:
        print(f"[!] Error: {e}")
        running = False
    finally:
        # Close the client socket
        if 'client_socket' in locals() and client_socket:
            client_socket.close()
        print("[*] Disconnected from server")

if __name__ == "__main__":
    main()
