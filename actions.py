import logging
from task import Task

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)

taks_list: list[Task] = []


def find_task_in_list(task_name: str):
    global taks_list
    for task in taks_list:
        if task.name == task_name:
            return task
    return None


def start(task_name: str):
    logger.info("starting ...")
    task = find_task_in_list(task_name)
    if task is not None:
        logger.info("Task " + task_name + " already started")
        return
    # call task.start
    # if success, add task to task list


def stop(task_name: str):
    logger.info("stoping ...")
    task = find_task_in_list(task_name)
    if task is None:
        logger.info("Task " + task_name + " not started")
        return
    # call task.stop


def restart(task_name: str):
    logger.info("restart")
    # find task in task list
    task = find_task_in_list(task_name)
    if task is None:
        logger.info("Task " + task_name + " not started")
        return
    # call task.restart


def status(task_name: str):
    logger.info("status")
    # find task in task list
    task = find_task_in_list(task_name)
    if task is None:
        logger.info("Task " + task_name + " not started")
        return
    # call task.status


def reload(task_name: str):
    logger.info("reload")
    # find task in task list
    task = find_task_in_list(task_name)
    if task is None:
        logger.info("Task " + task_name + " not started")
        return
    # call task.reload


def exit_action():
    logger.info("exiting ...")
    # call task.stop for each task
    for task in taks_list:
        task.stop()
        logger.info("Task " + task._name + " stopped")
    exit(0)
