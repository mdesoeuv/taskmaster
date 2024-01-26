import logging

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)
import signal
from actions import start, stop, restart, status, reload, exit_action

def command_interpreter(command: str):
    match command:
        case "start":
            start()
        case "stop":
            stop()
        case "restart":
            restart()
        case "status":
            status()
        case "reload":
            reload()
        case "exit":
            exit_action()
        case _:
            logger.info(
                "Unknown command: `"
                + command
                + "` (Available commands: start, stop, restart, reload, status, exit)"
            )

def sigint_handler(signum, frame):
    logger.info("\nSIGINT received, stopping...")
    exit_action()

def prompt():
    signal.signal(signal.SIGINT, sigint_handler)

    while True:
        command = input(">>> ")
        command_interpreter(command)
