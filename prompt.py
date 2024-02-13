import logging
import signal
from typing import List
from actions import (
    find_task_in_list,
    exit_action,
    reload_config_file,
    show_status
)
from task import Task

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)

task_list: List[Task] = []
config_file_path: str = ""


def command_interpreter(command: str):
    global task_list
    global config_file_path
    command = command.split()
    if len(command) == 0:
        return
    if len(command) == 1 and command[0] in ["exit", "reload"]:
        action = command[0]
    elif len(command) == 1:
        logger.info("Not enough arguments. usage: command [task_name]")
        return
    elif len(command) > 2:
        logger.info("Too many arguments. usage: command [task_name]")
        return
    else:
        action = command[0]
        task_name = command[1]
        task = find_task_in_list(task_name, task_list)
        if task is None:
            logger.info(f"Task {task_name} not in config file")
            return

    match action:
        case "start":
            task.start()
        case "stop":
            task.stop()
        case "restart":
            task.restart()
        case "status":
            show_status(task_list)
        case "reload":
            task_list = reload_config_file(config_file_path, task_list)
        case "exit":
            exit_action(task_list)
        case _:
            logger.info(
                f"Unknown command: `{action}` (Available commands: "
                "start, stop, restart, reload, status, exit)"
            )


def sigint_handler(signum: signal.Signals, frame):
    global task_list
    logger.info("\nSIGINT received, stopping...")
    exit_action(task_list)


def sighup_handler(signum: signal.Signals, frame):
    global task_list
    global config_file_path
    logger.info("\nSIGHUP received !")
    task_list = reload_config_file(config_file_path, task_list)


def prompt(start_task_list: list[Task], start_config_file_path: str):
    global task_list
    global config_file_path
    task_list = start_task_list
    config_file_path = start_config_file_path
    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGHUP, sighup_handler)
    while True:
        command = input(">>> ")
        command_interpreter(command)
