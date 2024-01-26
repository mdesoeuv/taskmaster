import logging
import signal
from actions import start, stop, restart, status, reload, exit_action

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def command_interpreter(command: str):
    command = command.split()
    if len(command) == 0:
        return
    if len(command) == 1 and command[0] != "exit":
        logger.info("Not enough arguments. usage: command [task_name]")
    elif len(command) > 2:
        logger.info("Too many arguments. usage: command [task_name]")
    else:
        action = command[0]
        task_name = command[1]

    match action:
        case "start":
            start(task_name)
        case "stop":
            stop(task_name)
        case "restart":
            restart(task_name)
        case "status":
            status(task_name)
        case "reload":
            reload(task_name)
        case "exit":
            exit_action()
        case _:
            logger.info(
                "Unknown command: `"
                + command
                + "` (Available commands: start, stop, restart, "
                + "reload, status, exit)"
            )


def sigint_handler(signum, frame):
    logger.info("\nSIGINT received, stopping...")
    exit_action()


def prompt():
    signal.signal(signal.SIGINT, sigint_handler)

    while True:
        command = input(">>> ")
        command_interpreter(command)
