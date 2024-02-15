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
) -> str:
    command = command.split()
    return_string = ""
    if len(command) == 0:
        return ""
    if len(command) == 1 and command[0] in ["exit", "reload", "status"]:
        action = command[0]
    elif len(command) == 1:
        logger.info("Not enough arguments. usage: command [task_name]")
        return "Not enough arguments. usage: command [task_name]"
    elif len(command) > 2:
        logger.info("Too many arguments. usage: command [task_name]")
        return "Too many arguments. usage: command [task_name]"
    else:
        action = command[0]
        process_group_name = command[1]
        task = find_process_in_list(process_group_name, process_groups)
        if task is None:
            logger.info(
                f"Process group {process_group_name} not in config file"
            )
            return f"Process group {process_group_name} not in config file"
    print(f"Command: {action}")

    match action:
        case "start":
            await task.start()
            return "Task started"
        case "stop":
            await task.stop()
            return "Task stopped"
        case "restart":
            await task.restart()
            return "Task restarted"
        case "status":
            return show_status(process_groups, return_string)
        case "reload":
            task_list = reload_config_file(config_file_path, process_groups)
            return "Config file reloaded"
        case "exit":
            exit_action(
                task_list
            )  # Assuming exit_action is synchronous. If not, add await.
        case _:
            logger.info(
                f"Unknown command: `{action}` (Available commands: "
                "start, stop, restart, reload, status, exit)"
            )
            return (
                f"Unknown command: `{action}` (Available commands: "
                "start, stop, restart, reload, status, exit)"
            )

    return "Command executed successfully"
