"""
TCP Chat Application - Common Module

This module contains shared functionality, constants, and utilities used by both
the client and server components of the TCP chat application.
"""

import socket
from datetime import datetime

# Network configuration
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 5555        # Port to listen on (non-privileged ports are > 1023)
BUFFER_SIZE = 1024  # Maximum message size

# Message types
class MessageType:
    """Enum-like class for message types to ensure consistent communication."""
    CHAT = "CHAT"           # Regular chat message
    SERVER = "SERVER"       # Server notification/information
    PRIVATE = "PRIVATE"     # Private message
    COMMAND_RESULT = "CMD"  # Result of a command
    ERROR = "ERROR"         # Error message
    USER_EVENT = "EVENT"    # User joined/left events

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

def format_message(message_type, content, sender=None, recipient=None):
    """
    Format a message with consistent structure for client-server communication.
    
    Args:
        message_type: Type of message (from MessageType class)
        content: The message content
        sender: The username of the sender (optional)
        recipient: The username of the recipient (for private messages)
        
    Returns:
        A formatted message string
    """
    timestamp = get_timestamp()
    
    if message_type == MessageType.CHAT and sender:
        return f"{timestamp} [{sender}] {content}"
    elif message_type == MessageType.PRIVATE and sender and recipient:
        return f"{timestamp} [PRIVATE FROM {sender}] {content}"
    elif message_type == MessageType.PRIVATE and sender:
        return f"{timestamp} [PRIVATE TO {recipient}] {content}"
    elif message_type == MessageType.SERVER:
        return f"{timestamp} [SERVER] {content}"
    elif message_type == MessageType.COMMAND_RESULT:
        return f"{timestamp} [SERVER] {content}"
    elif message_type == MessageType.ERROR:
        return f"{timestamp} [ERROR] {content}"
    elif message_type == MessageType.USER_EVENT:
        return f"{timestamp} [SERVER] {content}"
    else:
        return f"{timestamp} {content}"

def send_message(sock, message):
    """
    Send a message through a socket with error handling.
    
    Args:
        sock: The socket to send the message through
        message: The message to send
        
    Returns:
        True if successful, False otherwise
    """
    try:
        sock.send(message.encode('utf-8'))
        return True
    except Exception:
        return False
