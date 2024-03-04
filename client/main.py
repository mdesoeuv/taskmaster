# client.py
import socket
import readline
from typing import Tuple
import logging
from arg_parser import parse_server_port

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_command_valid(input_command: str) -> bool:
    command = input_command.split()

    match len(command):
        case 0:
            return False
        case 1:
            if command[0] not in ["exit", "reload", "status"]:
                logger.info("Not enough arguments. Usage: command [task_name]")
                return False
            else:
                return True
        case 2:
            return True
        case _:
            logger.info("Too many arguments. Usage: command [task_name]")
            return False


def send_command(address: Tuple[str, int]) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(address)
        print("Connected to the server. Type 'quit' to exit.")
        while True:
            try:
                command = input("> ").strip()
                if command.lower() == "quit":
                    break
                if is_command_valid(command):
                    s.sendall(command.encode())
                    response = s.recv(1024)
                    print(response.decode())
            except EOFError:
                print("\nexiting...")
                break  # Allows graceful exit with Ctrl+D
            except KeyboardInterrupt:
                print("\nexiting...")
                break


if __name__ == "__main__":
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = parse_server_port()
    send_command((HOST, PORT))
