import logging
from process_group import ProcessGroup
import pathlib
from config_parser import (
    config_file_parser,
    TaskDefinitionError,
    ConfigError,
    define_process_groups,
)

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def find_process_in_list(
    process_group_name: str, process_group_list: list[ProcessGroup]
):
    for process in process_group_list:
        if process.name == process_group_name:
            return process
    return None


def exit_action(process_groups: list[ProcessGroup]):
    logger.info("Exiting all processes...")
    for process_group in process_groups:
        process_group.stop()
    exit(0)


def are_process_groups_different(
    old_process_group: ProcessGroup, new_process_group: ProcessGroup
) -> bool:
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
        old_attr = getattr(old_process_group, attr)
        new_attr = getattr(new_process_group, attr)
        if old_attr != new_attr:
            return True

    return False


def reload_config_file(
    file_path: str, old_process_groups: list[ProcessGroup]
) -> list[ProcessGroup]:
    logger.info("Reloading config file...")
    updated_process_group_list = []
    try:
        new_config = config_file_parser(pathlib.Path(file_path))
        new_process_group_list = define_process_groups(new_config)

        for old_process_group in old_process_groups:
            new_process_group: ProcessGroup | None = find_process_in_list(
                old_process_group.name, new_process_group_list
            )
            if new_process_group:
                # old process group with new config
                if are_process_groups_different(
                    old_process_group, new_process_group
                ):
                    logger.info(
                        f"Process group {new_process_group.name} has changed. Reloading process group..."
                    )
                    old_process_group.stop()
                    updated_process_group_list.append(new_process_group)
                    new_process_group.start()
                    logger.info(
                        f"Process group {new_process_group.name} reloaded"
                    )
                # old process group without changes
                else:
                    logger.info(
                        f"Process group {new_process_group.name} unchanged"
                    )
                    updated_process_group_list.append(old_process_group)
            # old process group that is no longer in config
            else:
                old_process_group.stop()
        # new process groups which where not in old process group list
        for new_process_group in new_process_group_list:
            updated_process_group: ProcessGroup | None = find_process_in_list(
                new_process_group.name, updated_process_group_list
            )
            if not updated_process_group:
                logger.info(
                    f"New Process group {new_process_group.name} to add"
                )
                updated_process_group_list.append(new_process_group)
                new_process_group.start()

        logger.info("Config file reloaded successfully")
    except (TaskDefinitionError, ConfigError) as e:
        print(f"Error reloading config file: {e}")
    return updated_process_group_list


def show_status(process_groups: list[ProcessGroup], return_string: str) -> str:
    for process_group in process_groups:
        return_string += f"{process_group.get_status()}\n"
        print(return_string)
    return return_string
