import asyncio
import logging
import signal
from typing import List
from actions import (
    find_task_in_list,
    exit_action,
    reload_config_file,
    show_status,
)
from server.process import ProcessGroup

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)

task_list: List[ProcessGroup] = []
config_file_path: str = ""


async def command_interpreter(command: str):
    global task_list
    global config_file_path
    command = command.split()
    if len(command) == 0:
        return
    if len(command) == 1 and command[0] in ["exit", "reload", "status"]:
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
            await task.start()
        case "stop":
            await task.stop()
        case "restart":
            await task.restart()
        case "status":
            show_status(
                task_list
            )  # Assuming show_status is synchronous. If not, add await.
        case "reload":
            task_list = reload_config_file(config_file_path, task_list)
        case "exit":
            exit_action(
                task_list
            )  # Assuming exit_action is synchronous. If not, add await.
        case _:
            logger.info(
                f"Unknown command: `{action}` (Available commands: "
                "start, stop, restart, reload, status, exit)"
            )


async def async_input(prompt):
    print(prompt, end="", flush=True)
    return await asyncio.get_event_loop().run_in_executor(None, input)


async def signal_handler(name):
    global task_list
    logger.info(f"\n{name} received !")
    if name == "SIGINT":
        exit_action(
            task_list
        )  # Assuming exit_action is synchronous. If not, make it async and await it.
    elif name == "SIGHUP":
        task_list = reload_config_file(
            config_file_path, task_list
        )  # Assuming synchronous. If not, await it.


async def prompt(
    start_task_list: list[ProcessGroup], start_config_file_path: str
):
    global task_list
    global config_file_path
    task_list = start_task_list
    config_file_path = start_config_file_path
    loop = asyncio.get_event_loop()
    for signame in ("SIGINT", "SIGHUP"):
        loop.add_signal_handler(
            getattr(signal, signame),
            lambda: asyncio.create_task(signal_handler(signame)),
        )

    while True:
        command = await async_input(">>> ")
        await command_interpreter(command)
