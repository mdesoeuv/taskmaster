import logging
import signal
from actions import (
    find_task_in_list,
    exit_action,
)

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def command_interpreter(command: str):
    command = command.split()
    if len(command) == 0:
        return
    if len(command) == 1 and command[0] == "exit":
        action = command[0]
    elif len(command) == 1:
        logger.info("Not enough arguments. usage: command [task_name]")
    elif len(command) > 2:
        logger.info("Too many arguments. usage: command [task_name]")
    else:
        action = command[0]
        task_name = command[1]
        task = find_task_in_list(task_name)
        if task is None:
            logger.info("Task " + task_name + " not in config file")
            return

    match action:
        case "start":
            task.start()
        case "stop":
            task.stop()
        case "restart":
            task.restart()
        case "status":
            task.status()
        case "reload":
            task.reload()
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
