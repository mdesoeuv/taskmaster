# server.py
import socket
from typing import Tuple


def handle_client(conn, addr):
    print(f"Connected by {addr}")
    with conn:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break  # Break the loop if no data is sent by the client.
            response = (
                "status"
                if data == "status"
                else "start" if data == "start" else "Unrecognized command"
            )
            conn.sendall(response.encode())
    print(f"Connection with {addr} closed.")


def start_server(address: Tuple[str, int]) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(address)
        s.listen()
        print(f"Listening on {address}")
        while True:  # Loop forever to accept all incoming connections
            conn, addr = s.accept()
            handle_client(conn, addr)  # Handle the client in a function


if __name__ == "__main__":
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 65433  # Port to listen on (non-privileged ports are > 1023)
    start_server((HOST, PORT))
