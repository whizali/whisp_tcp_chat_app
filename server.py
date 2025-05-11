#!/usr/bin/env python3
"""
TCP Chat Application - Server
Computer Networks Course Project

This module implements the server side of a TCP-based chat application using select-based I/O multiplexing.
It includes enhanced features like username registration, timestamped messages, and command support.
"""
import socket
import select
import sys
import time
from datetime import datetime

# Server configuration
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 5555        # Port to listen on (non-privileged ports are > 1023)
BUFFER_SIZE = 1024  # Maximum message size

# Dictionary to store client information
# Key: socket object, Value: (address, username)
clients = {}

# Dictionary to store pending username registrations
# Key: socket object, Value: True/False (waiting for username)
pending_registrations = {}

# Counter for assigning default usernames
user_counter = 0

# Available commands
COMMANDS = {
    '/help': 'Show available commands',
    '/list': 'List all connected users',
    '/whisper': 'Send a private message to a user: /whisper <username> <message>',
    '/exit': 'Disconnect from the server',
    '/nick': 'Change your username: /nick <new_username>'
}

def get_timestamp():
    """Get a formatted timestamp for messages."""
    return datetime.now().strftime('[%H:%M:%S]')

def get_username(client_socket):
    """Get the username for a client socket."""
    if client_socket in clients and clients[client_socket][1]:
        return clients[client_socket][1]
    else:
        client_address = clients[client_socket][0]
        return f"{client_address[0]}:{client_address[1]}"

def broadcast_message(message, sender_socket=None, include_timestamp=True):
    """
    Broadcast a message to all connected clients except the sender.

    Args:
        message: The message to broadcast
        sender_socket: The socket of the client who sent the message (to avoid echo)
        include_timestamp: Whether to include a timestamp in the message
    """
    if include_timestamp:
        message = f"{get_timestamp()} {message}"

    for client_socket in clients:
        # Don't send the message back to the sender
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode('utf-8'))
            except Exception:
                # If sending fails, the client might be disconnected
                # We'll handle this in the main loop
                pass

def send_private_message(message, sender_socket, recipient_username):
    """
    Send a private message to a specific user.

    Args:
        message: The message to send
        sender_socket: The socket of the client who sent the message
        recipient_username: The username of the recipient

    Returns:
        True if the message was sent, False otherwise
    """
    sender_username = get_username(sender_socket)
    timestamp = get_timestamp()

    # Find the recipient socket
    recipient_socket = None
    for sock, (_, username) in clients.items():
        if username == recipient_username:
            recipient_socket = sock
            break

    if recipient_socket:
        try:
            # Format the private message
            private_message = f"{timestamp} [PRIVATE FROM {sender_username}] {message}"
            recipient_socket.send(private_message.encode('utf-8'))

            # Also send a confirmation to the sender
            confirmation = f"{timestamp} [PRIVATE TO {recipient_username}] {message}"
            sender_socket.send(confirmation.encode('utf-8'))
            return True
        except Exception:
            return False
    else:
        # User not found
        error_message = f"{timestamp} [SERVER] User '{recipient_username}' not found."
        sender_socket.send(error_message.encode('utf-8'))
        return False

def handle_command(client_socket, command):
    """
    Handle a command from a client.

    Args:
        client_socket: The client's socket object
        command: The command string

    Returns:
        True if the command was handled, False if it's not a command
    """
    if not command.startswith('/'):
        return False

    parts = command.split(' ', 1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    timestamp = get_timestamp()
    username = get_username(client_socket)

    if cmd == '/help':
        # Send help information
        help_text = f"{timestamp} [SERVER] Available commands:\n"
        for cmd, desc in COMMANDS.items():
            help_text += f"  {cmd} - {desc}\n"
        client_socket.send(help_text.encode('utf-8'))

    elif cmd == '/list':
        # List all connected users
        user_list = f"{timestamp} [SERVER] Connected users ({len(clients)}):\n"
        for _, (_, user) in enumerate(clients.values()):
            if user:  # Only list users who have registered a username
                user_list += f"  - {user}\n"
        client_socket.send(user_list.encode('utf-8'))

    elif cmd == '/whisper':
        # Send a private message
        # First, check if we have enough arguments
        if ' ' not in args:
            client_socket.send(f"{timestamp} [SERVER] Usage: /whisper <username> <message>".encode('utf-8'))
            return True

        # Special handling for usernames with spaces (like "User 2")
        # Try to find a matching username from our clients dictionary
        recipient = None
        message = None

        # Get all usernames
        all_usernames = [username for _, username in clients.values() if username]

        # Sort usernames by length (descending) to match longer usernames first
        all_usernames.sort(key=len, reverse=True)

        # Try to find a matching username at the beginning of args
        for username in all_usernames:
            if args.startswith(username + ' '):
                recipient = username
                message = args[len(username) + 1:]  # +1 for the space
                break

        # If no username was found, try the traditional approach
        if recipient is None:
            whisper_parts = args.split(' ', 1)
            recipient = whisper_parts[0]
            message = whisper_parts[1] if len(whisper_parts) > 1 else ""

        # Send the private message
        if message:
            send_private_message(message, client_socket, recipient)
        else:
            client_socket.send(f"{timestamp} [SERVER] Usage: /whisper <username> <message>".encode('utf-8'))
            return True

    elif cmd == '/exit':
        # Client wants to exit - this will be handled in the main loop
        # Just send a confirmation
        client_socket.send(f"{timestamp} [SERVER] Disconnecting...".encode('utf-8'))
        return False  # Let the client close the connection

    elif cmd == '/nick':
        # Change username
        if not args:
            client_socket.send(f"{timestamp} [SERVER] Usage: /nick <new_username>".encode('utf-8'))
            return True

        new_username = args.strip()

        # Check if username is already taken
        for _, (_, user) in clients.items():
            if user == new_username:
                client_socket.send(f"{timestamp} [SERVER] Username '{new_username}' is already taken.".encode('utf-8'))
                return True

        # Update username
        old_username = clients[client_socket][1]
        clients[client_socket] = (clients[client_socket][0], new_username)

        # Notify the client
        client_socket.send(f"{timestamp} [SERVER] Your username has been changed to '{new_username}'.".encode('utf-8'))

        # Notify other clients
        if old_username:
            broadcast_message(f"[SERVER] User '{old_username}' is now known as '{new_username}'.", client_socket)
        else:
            broadcast_message(f"[SERVER] User {username} is now known as '{new_username}'.", client_socket)

    else:
        # Unknown command
        client_socket.send(f"{timestamp} [SERVER] Unknown command: {cmd}. Type /help for available commands.".encode('utf-8'))

    return True

def handle_new_connection(server_socket):
    """
    Accept a new client connection.

    Args:
        server_socket: The server's socket object

    Returns:
        The new client socket object
    """
    global user_counter

    # Accept the connection
    client_socket, client_address = server_socket.accept()

    # Set the socket to non-blocking mode
    client_socket.setblocking(0)

    # Increment user counter and assign default username
    user_counter += 1
    default_username = f"User {user_counter}"

    # Store client information with default username
    client_id = f"{client_address[0]}:{client_address[1]}"
    clients[client_socket] = (client_address, default_username)

    # No need to mark as pending since we've assigned a default username
    # But we'll still allow the user to change it

    print(f"[+] Accepted connection from {client_id} (assigned username: {default_username})")

    # Send a welcome message to the new client
    timestamp = get_timestamp()
    welcome_message = f"{timestamp} [SERVER] Welcome to the TCP Chat Server! There are {len(clients)} clients connected."
    client_socket.send(welcome_message.encode('utf-8'))

    # Inform the user of their default username and how to change it
    username_message = f"{timestamp} [SERVER] You have been assigned the username '{default_username}'. You can change it using the /nick command."
    client_socket.send(username_message.encode('utf-8'))

    # Notify other clients about the new user
    broadcast_message(f"[SERVER] User '{default_username}' has joined the chat.", client_socket)

    return client_socket

def handle_client_message(client_socket):
    """
    Handle a message from a client.

    Args:
        client_socket: The client's socket object

    Returns:
        True if the client is still connected, False otherwise
    """
    client_address = clients[client_socket][0]
    client_id = f"{client_address[0]}:{client_address[1]}"

    try:
        # Receive data from the client
        data = client_socket.recv(BUFFER_SIZE)

        # If no data is received, the client has disconnected
        if not data:
            return False

        # Decode the received data
        message = data.decode('utf-8').strip()

        # Check if this is a command
        if message.startswith('/'):
            print(f"[>] Command from {get_username(client_socket)}: {message}")
            handle_command(client_socket, message)
            return True

        # Regular message
        print(f"[>] Message from {get_username(client_socket)}: {message}")

        # Format the message with the username
        username = get_username(client_socket)
        formatted_message = f"[{username}] {message}"

        # Broadcast the message to all other clients
        broadcast_message(formatted_message, client_socket)

        return True

    except Exception as e:
        print(f"[!] Error handling client {client_id}: {e}")
        return False

def remove_client(client_socket):
    """
    Remove a client from the server.

    Args:
        client_socket: The client's socket object
    """
    # Get client information before removing
    if client_socket in clients:
        client_address = clients[client_socket][0]
        username = clients[client_socket][1] or f"{client_address[0]}:{client_address[1]}"

        # Remove the client from our dictionaries
        del clients[client_socket]
        if client_socket in pending_registrations:
            del pending_registrations[client_socket]

        # Close the client socket
        client_socket.close()

        # Notify everyone that the client has left
        leave_message = f"[SERVER] User '{username}' has left the chat."
        print(leave_message)
        broadcast_message(leave_message)

        print(f"[-] Connection with {username} closed. {len(clients)} clients remaining.")

def main():
    """Main function to start the server."""
    print(f"[*] Starting TCP Chat Server on {HOST}:{PORT}")

    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set socket option to reuse address (helps avoid "Address already in use" errors)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Set the server socket to non-blocking mode
    server_socket.setblocking(0)

    try:
        # Bind the socket to the address and port
        server_socket.bind((HOST, PORT))

        # Listen for incoming connections (queue up to 5 connection requests)
        server_socket.listen(5)
        print(f"[*] Listening for connections on {HOST}:{PORT}")
        print(f"[*] Server started at {get_timestamp()}")

        # List of sockets to monitor for input
        inputs = [server_socket]

        while inputs:
            try:
                # Use select to monitor sockets for input
                # The timeout (1 second) allows for keyboard interrupts to be caught
                readable, _, exceptional = select.select(inputs, [], inputs, 1)

                # Handle readable sockets (sockets with data to read)
                for sock in readable:
                    # If the server socket is readable, a new connection is coming in
                    if sock is server_socket:
                        # Accept the new connection
                        new_client = handle_new_connection(server_socket)
                        # Add the new client to our list of inputs to monitor
                        inputs.append(new_client)
                    # Otherwise, an existing client is sending a message
                    else:
                        # Handle the client message
                        still_connected = handle_client_message(sock)
                        # If the client has disconnected, remove it
                        if not still_connected:
                            remove_client(sock)
                            inputs.remove(sock)

                # Handle exceptional sockets (sockets with errors)
                for sock in exceptional:
                    # Remove the socket with an error
                    if sock in inputs:
                        inputs.remove(sock)
                    remove_client(sock)

            except KeyboardInterrupt:
                print("\n[!] Server interrupted by user")
                break

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        # Close all client sockets
        for sock in clients:
            sock.close()

        # Close the server socket
        if server_socket:
            server_socket.close()

        print("[*] Server is shutting down")

if __name__ == "__main__":
    main()
