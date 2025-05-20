# TCP Chat Application

A Python-based TCP chat application developed for the Computer Networks course. This application demonstrates fundamental networking concepts including TCP socket programming, client-server architecture, and non-blocking I/O with select().

## Overview

This application implements a real-time chat system where multiple clients can connect to a central server, register usernames, send public and private messages, and use various commands. The system uses TCP sockets for reliable communication and implements select()-based I/O multiplexing st the server side for efficient handling of multiple client connections and threading at client side for parralel and simultaneous sending and receiving of messages.

## Features

- **TCP-based Client-Server Communication**: Reliable, connection-oriented messaging
- **Multiple Client Support**: Handles numerous concurrent client connections
- **Automatic Username Assignment**: Clients are assigned default usernames (User 1, User 2, etc.) upon connection
- **Username Customization**: Clients can change their default usernames using the `/nick` command
- **Timestamped Messages**: All messages include timestamps for chronological tracking
- **Command Support**: Implements various commands for enhanced functionality:
  - `/help` - Display available commands
  - `/list` - List all connected users
  - `/whisper <username> <message>` - Send private messages
  - `/exit` - Disconnect from the server
  - `/nick <new_username>` - Change username
- **Graceful Disconnection Handling**: Properly manages client disconnections
- **Non-blocking I/O**: Uses select() for efficient socket monitoring

## Core Networking Concepts

### TCP Socket Programming

The application uses TCP (Transmission Control Protocol) sockets for reliable, connection-oriented communication:

- **Connection Establishment**: Implements the TCP three-way handshake process
  **3-way handshake process happening at OS TCP/IP level**:
  - Client sends a SYN packet to the server in client_socket.connect((SERVER_HOST, SERVER_PORT)) call. the SYN flag is set to 1, indicating a request to synchronize sequence numbers and is used to start the connection process.
  -  server_socket.listen(5) state listens for incoming connections. When server_socket.accept() is called (inside  handle_new_connection), the server's TCP stack sends an acknowledgment (ACK) flag set to 1 in the SYN-ACK packet back to the client.
  - Client sends an ACK packet to complete the handshake in response of the SYN-ACK packet. When this ACK is received, the connection is established. The accept() call completes, returning a new socket for the established connection.

  **In the TCP Chat Application, the SYN and ACK flags are handled automatically by the operating system's TCP/IP stack when socket operations like connect(), accept(), and send()/recv() are called, enabling reliable communication between the chat clients and server.**

- **Reliable Data Transfer**: Ensures messages are delivered in order without loss
- **Connection Termination**: Properly closes connections to free resources

### Client-Server Architecture

The system follows a centralized client-server model:

- **Server**: Acts as a central hub that:
  - Listens for incoming connections
  - Manages client connections
  - Processes and routes messages
  - Maintains client information
- **Clients**: End-user applications that:
  - Connect to the server
  - Send messages and commands
  - Receive and display messages from other clients

### I/O Multiplexing with select()

Instead of using one thread per client (which can be resource-intensive), the server uses select()-based I/O multiplexing:

- **Non-blocking Socket Operations**: Sockets are set to non-blocking mode
- **Socket Monitoring**: The select() function monitors multiple sockets simultaneously
- **Event-driven Processing**: Only processes sockets that have data ready to be read
- **Efficient Resource Usage**: Handles many connections with minimal system resources

### Message Protocol

The application implements a simple text-based protocol:

- **Message Format**: Plain text with timestamps and sender information
- **Command Prefixing**: Commands are prefixed with `/` (e.g., `/help`)
- **Private Messaging**: Special format for private messages
- **UTF-8 Encoding**: All messages are encoded/decoded using UTF-8

## Communication Flow

### Server Startup

1. Server creates a TCP socket
2. Socket is set to non-blocking mode and configured to reuse address
3. Server binds to the specified host and port
4. Server starts listening for incoming connections
5. Server initializes the socket monitoring list with the server socket

### Client Connection Process

1. Client creates a TCP socket
2. Client attempts to connect to the server (with timeout)
3. Upon successful connection:
   - Server accepts the connection
   - Server adds the client socket to the monitoring list
   - Server assigns a default username (User 1, User 2, etc.)
   - Server sends a welcome message
   - Server informs the client of their default username
4. Server associates the default username with the client socket
5. Server notifies all clients about the new user
6. Client can optionally change their username using the `/nick` command

### Message Exchange

1. **Client to Server**:
   - Client enters a message
   - Message is encoded and sent to the server
   - Server receives and processes the message

2. **Server Processing**:
   - Server checks if the message is a command
   - If it's a command, server executes the appropriate action
   - If it's a regular message, server formats it with timestamp and username

3. **Server to Clients**:
   - For regular messages: server broadcasts to all other clients
   - For private messages: server sends only to the specified recipient
   - For command responses: server sends back to the originating client

### Disconnection Process

1. Client sends `/exit` command or closes the connection
2. Server detects the disconnection
3. Server removes the client from the monitoring list
4. Server removes client information from storage
5. Server notifies other clients about the disconnection
6. Server closes the client socket

## Implementation Details

### Common Module (`common.py`)

- **Shared Constants**:
  - Network configuration (host, port, buffer size)
  - Command definitions
  - Message type definitions

- **Message Formatting**:
  - Consistent message formatting across client and server
  - Timestamp generation
  - Message type categorization (chat, server, private, etc.)

- **Utilities**:
  - Helper functions for common operations
  - Network communication utilities

### Server Side (`server.py`)

- **Socket Management**:
  - Creates, configures, and manages the server socket
  - Maintains a list of client sockets to monitor
  - Uses select() to efficiently handle multiple connections

- **Client Management**:
  - Stores client information (address, username) in a dictionary
  - Handles client disconnections
  - Assigns default usernames

- **Message Handling**:
  - Receives and processes messages from clients
  - Formats messages with appropriate types
  - Broadcasts messages to appropriate recipients
  - Server-side logging separate from client communication

- **Command Processing**:
  - Parses and executes commands
  - Sends appropriate responses back to clients

### Client Side (`client.py`)

- **Connection Management**:
  - Establishes and maintains connection to the server
  - Implements timeout for connection attempts
  - Handles disconnection gracefully

- **Message Handling**:
  - Uses a separate thread for receiving messages
  - Sends user input to the server
  - Displays received messages without server-side logs
  - Client-side logging separate from user interface

- **User Interface**:
  - Provides command-line interface for user interaction
  - Displays help information for available commands
  - Shows status messages for connection events

## How to Run

### Server

```bash
python server.py
```

### Client

```bash
python client.py
```

## Project Structure

```
tcp_chat_app/
├── server.py - Server implementation with select()-based I/O
├── client.py - Client implementation with threading for message reception
├── common.py - Shared utilities, constants, and message formatting
├── README.md - Documentation
├── diagrams/ - Visual documentation of application flow
└── requirements.txt - Dependencies
```

## Requirements

- Python 3.6+
- Standard library modules: socket, select, threading, datetime, logging

## Future Enhancements

- **GUI Implementation**: A graphical user interface using Tkinter or PyQt
- **Message Encryption**: End-to-end encryption for secure communication
- **File Transfer**: Capability to send and receive files
- **Chat Rooms**: Support for multiple chat rooms or channels
- **User Authentication**: Login system with passwords
