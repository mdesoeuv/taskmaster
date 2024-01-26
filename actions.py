import logging
from task import Task

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)

task_list: list[Task] = []


def find_task_in_list(task_name: str):
    global task_list
    for task in task_list:
        if task.name == task_name:
            return task
    return None


def exit_action():
    logger.info("exiting ...")
    # call task.stop for each task
    for task in task_list:
        task.stop()
        logger.info("Task " + task._name + " stopped")
    exit(0)
