import logging
from task import Task
import pathlib
from config_parser import (
    config_file_parser,
    TaskDefinitionError,
    ConfigError,
    define_tasks,
)

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


def is_task_in_list(task_list: list[Task], task_name: str) -> bool:
    res: bool = False
    for task in task_list:
        if task.name == task_name:
            res = True
            break
    return res


def are_tasks_different(old_task: Task, new_task: Task) -> bool:
    # Compare only the specified attributes
    attrs_to_compare = [
        "name",
        "cmd",
        "numprocs",
        "umask",
        "workingdir",
        "autostart",
        "autorestart",
        "exitcodes",
        "startretries",
        "starttime",
        "stopsignal",
        "stoptime",
        "stdout",
        "stderr",
        "env",
    ]

    for attr in attrs_to_compare:
        old_attr = getattr(old_task, attr)
        new_attr = getattr(new_task, attr)
        if old_attr != new_attr:
            return True

    return False


def reload_config_file(
    file_path: str, old_task_list: list[Task]
) -> list[Task]:
    logger.info("Reloading config file...")
    updated_task_list = []
    try:
        new_config = config_file_parser(pathlib.Path(file_path))
        new_tasks_list = define_tasks(new_config)

        for old_task in old_task_list:
            new_task: Task | None = find_task_in_list(
                old_task.name, new_tasks_list
            )
            if new_task:
                # old task with new config
                if are_tasks_different(old_task, new_task):
                    logger.info(
                        f"Task {new_task.name} has changed. Reloading task..."
                    )
                    old_task.stop()
                    updated_task_list.append(new_task)
                    new_task.start()
                    logger.info(f"Task {new_task.name} reloaded")
                # old task without changes
                else:
                    logger.info(f"Task {new_task.name} unchanged")
                    updated_task_list.append(old_task)
            # old task that is no longer in config
            else:
                old_task.stop()
        # new tasks which where not in old task list
        for new_task in new_tasks_list:
            updated_task: Task | None = find_task_in_list(
                new_task.name, updated_task_list
            )
            if not updated_task:
                logger.info(f"New task {new_task.name} to add")
                updated_task_list.append(new_task)
                new_task.start()

        logger.info("Config file reloaded successfully")
    except (TaskDefinitionError, ConfigError) as e:
        print(f"Error reloading config file: {e}")
    return updated_task_list


def show_status(task_list: list[Task]):
    for task in task_list:
        print(task.get_status())