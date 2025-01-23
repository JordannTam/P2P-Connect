# P2PConnect - Peer-to-Peer Communication System

A distributed network application enabling secure file transfer and communication between edge devices.

## Features
- Secure user authentication with account lockout protection
- P2P file transfer between edge devices
- Multi-threaded architecture supporting concurrent connections
- Command-driven interface for device operations
- Real-time file generation and transfer
- Robust logging system

## Requirements
- Python 3.x
- Socket library
- Threading library

## Installation
```bash
git clone https://github.com/JordannTam/P2PConnect.git
cd P2PConnect
```

## Usage
1. Start the server:
```bash
python3 server.py <server_port> <max_login_attempts>
```

2. Start clients:
```bash
python3 client.py <server_IP> <server_port> <client_udp_port>
```

## Commands
- `EDG` - Generate data on edge device
- `UED` - Upload edge device data
- `SCS` - Server computation service
- `DTE` - Delete file
- `AED` - List active edge devices
- `UVF` - Upload file to another device
- `OUT` - Exit

## Architecture
- Multi-threaded server handling concurrent client connections
- UDP/TCP socket implementation
- Thread-safe authentication system
- Distributed P2P communication protocol

## License
MIT License