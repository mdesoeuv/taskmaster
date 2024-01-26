import logging
from task import Task

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def find_task_in_list(task_name: str, task_list: list[Task]):
    for task in task_list:
        if task.name == task_name:
            return task
    return None


def exit_action(task_list: list[Task]):
    logger.info("Exiting all tasks...")
    for task in task_list:
        task.stop()
    exit(0)


def reload_config_file(file_path: str, task_list: list[Task]):
    logger.info("Reloading config file...")
    # VICTOR
    # abort reload if new config file is invalid
    # stop all tasks removed from new config
    # add new tasks only from new config to task list after starting them
    # update new parameters for remaining tasks, restart them if necessary
    new_task_list = task_list
    logger.info("Config file reloaded successfully")
    return new_task_list