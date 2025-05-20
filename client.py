"""
TCP Chat Application - Client

This module implements the client side of a TCP-based chat application.
It connects to the server and supports username registration, commands, and private messaging.
"""

import socket
import threading
import logging

# Import common utilities and constants
from common import (
    HOST as SERVER_HOST,
    PORT as SERVER_PORT,
    BUFFER_SIZE,
    COMMANDS
)

# Configure client logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [CLIENT] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('client')

# Global variables
running = True  # Flag to control the receive thread
username = None  # The client's username

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
                    logger.warning("Server disconnected")
                    running = False
                    break

                # Decode the received message
                message = data.decode('utf-8')

                # Process username assignment/change messages
                if "You have been assigned the username '" in message and username is None:
                    # Extract the default username from the message
                    start_index = message.find("You have been assigned the username '") + len("You have been assigned the username '")
                    end_index = message.find("'.", start_index)
                    if start_index > 0 and end_index > start_index:
                        username = message[start_index:end_index]
                        print(f"\n{message}")
                        logger.info(f"Default username set to '{username}'")
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
                        logger.info(f"Username successfully changed to '{username}'")
                    else:
                        print(f"\n{message}")

                # Handle error messages
                elif "[ERROR]" in message:
                    print(f"\n{message}")
                    # Log client-side but don't show server logs
                    if "Username '" in message and "' is already taken" in message:
                        logger.warning("Username change failed - already taken")

                # Handle private messages
                elif "[PRIVATE" in message:
                    print(f"\n{message}")

                # Handle regular chat messages
                else:
                    # Print the message with a newline to avoid overwriting the input prompt
                    print(f"\n{message}")

                # Reprint the input prompt
                print("Enter message (or '/help' for commands): ", end='', flush=True)

            except ConnectionResetError:
                print("\n[!] Connection reset by server")
                logger.error("Connection reset by server")
                running = False
                break

    except Exception as e:
        print(f"\n[!] Error receiving messages: {e}")
        logger.error(f"Error receiving messages: {e}")
        running = False

def main():
    """Main function to start the client."""
    global running, username

    logger.info(f"Connecting to TCP Chat Server at {SERVER_HOST}:{SERVER_PORT}")
    print(f"Connecting to TCP Chat Server at {SERVER_HOST}:{SERVER_PORT}")

    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set a timeout for connection attempts
        client_socket.settimeout(10)

        # Connect to the server
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        logger.info(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")
        print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")

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
                logger.info("Disconnecting...")
                print("Disconnecting...")
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
                    logger.info(f"Requesting username change to '{requested_username}'...")

    except ConnectionRefusedError:
        error_msg = f"Connection refused. Make sure the server is running at {SERVER_HOST}:{SERVER_PORT}"
        logger.error(error_msg)
        print(f"[!] {error_msg}")
    except socket.timeout:
        error_msg = f"Connection attempt timed out. Server might be busy or unreachable."
        logger.error(error_msg)
        print(f"[!] {error_msg}")
    except KeyboardInterrupt:
        logger.info("Client interrupted by user")
        print("\n[!] Client interrupted by user")
        running = False
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"[!] Error: {e}")
        running = False
    finally:
        # Close the client socket
        if 'client_socket' in locals() and client_socket:
            client_socket.close()
        logger.info("Disconnected from server")
        print("Disconnected from server")

if __name__ == "__main__":
    main()
