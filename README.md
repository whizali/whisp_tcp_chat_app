# TCP Chat Application

A Python-based TCP chat application developed for the Computer Networks course.

## Overview

This application demonstrates the implementation of a client-server architecture using TCP sockets in Python. It allows multiple clients to connect to a central server and exchange messages in real-time.

## Features (Planned)

- Basic client-server communication
- Support for multiple clients
- Username registration
- Timestamped messages
- Command support (e.g., `/exit`, `/list`)
- Graceful disconnection handling

## Technical Concepts

- TCP socket programming
- Client-server architecture
- Multithreading for handling multiple clients
- I/O multiplexing with `select()`

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
├── server.py - Server implementation
├── client.py - Client implementation
├── README.md - Documentation
└── requirements.txt - Dependencies
```

## Requirements

- Python 3.6+
- Standard library modules: socket, threading, select
