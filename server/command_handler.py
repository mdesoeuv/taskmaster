from process_group import ProcessGroup
from actions import (
    find_process_in_list,
    show_status,
    reload_config_file,
    exit_action,
)
import logging

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


async def handle_command(
    command: str, process_groups: list[ProcessGroup], config_file_path: str
):
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
        process_group_name = command[1]
        task = find_process_in_list(process_group_name, process_groups)
        if task is None:
            logger.info(
                f"Process group {process_group_name} not in config file"
            )
            return

    match action:
        case "start":
            await process_group_name.start()
        case "stop":
            await process_group_name.stop()
        case "restart":
            await process_group_name.restart()
        case "status":
            show_status(process_groups)
        case "reload":
            task_list = reload_config_file(config_file_path, process_groups)
        case "exit":
            exit_action(
                task_list
            )  # Assuming exit_action is synchronous. If not, add await.
        case _:
            logger.info(
                f"Unknown command: `{action}` (Available commands: "
                "start, stop, restart, reload, status, exit)"
            )
