from actions import (
    show_status,
    reload_config_file,
    shutdown,
    list_programs
)
import logging

from taskmaster import TaskMaster

logger = logging.getLogger(__name__)


async def handle_command(
    command: str, taskmaster: TaskMaster, root_logger: logging.Logger
) -> str:
    logger.debug(f"Command: {command}")
    command = command.split()
    return_string = ""
    if len(command) == 0:
        return ""
    if len(command) == 1 and command[0] in ["shutdown", "reload", "status", "list"]:
        action = command[0]
    elif len(command) == 1:
        logger.info(
            "Not enough arguments. usage: command [task_name or loglevel]"
        )
        return "Not enough arguments. usage: command [task_name]"
    elif len(command) > 2:
        logger.info("Too many arguments. usage: command [task_name]")
        return "Too many arguments. usage: command [task_name]"
    elif command[0] == "loglevel":
        action = command[0]
        log_level = command[1].upper()
        if log_level not in [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]:
            return f"Invalid log level: {command[1].upper()}, valid log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    else:
        action = command[0]
        program_name = command[1]
        task = taskmaster.programs.get(program_name)
        if task is None:
            logger.info(f"Process group {program_name} not in config file")
            return f"Process group {program_name} not in config file"

    match action:
        case "start":
            return task.start()
        case "stop":
            return task.stop()
        case "restart":
            return task.restart()
        case "status":
            return show_status(taskmaster.programs, return_string)
        case "reload":
            return await reload_config_file(taskmaster)
        case "shutdown":
            return await shutdown(taskmaster)
        case "list":
            return list_programs(taskmaster.programs, return_string)
        case "loglevel":
            log_level = command[1].upper()
            root_logger.setLevel(getattr(logging, log_level))
            logger.info(f"Log level set to {log_level}")
            return f"Log level set to {log_level}"
        case _:
            logger.info(
                f"Unknown command: `{action}` (Available commands: "
                "start, stop, restart, reload, status, exit)"
            )
            return (
                f"Unknown command: `{action}` (Available commands: "
                "start, stop, restart, reload, status, exit)"
            )
