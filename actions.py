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
        logger.info("Task " + task.name + " stopped")
    exit(0)
