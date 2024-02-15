import logging
from program import Program
import pathlib
from config_parser import (
    config_file_parser,
    TaskDefinitionError,
    ConfigError,
    define_programs,
)

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def find_process_in_list(program_name: str, program_list: list[Program]):
    for process in program_list:
        if process.name == program_name:
            return process
    return None


def exit_action(programs: list[Program]):
    logger.info("Exiting all processes...")
    for program in programs:
        program.stop()
    exit(0)


def are_programs_different(old_program: Program, new_program: Program) -> bool:
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
        old_attr = getattr(old_program, attr)
        new_attr = getattr(new_program, attr)
        if old_attr != new_attr:
            return True

    return False


def reload_config_file(
    file_path: str, old_programs: list[Program]
) -> list[Program]:
    logger.info("Reloading config file...")
    updated_program_list = []
    try:
        new_config = config_file_parser(pathlib.Path(file_path))
        new_program_list = define_programs(new_config)

        for old_program in old_programs:
            new_program: Program | None = find_process_in_list(
                old_program.name, new_program_list
            )
            if new_program:
                # old process group with new config
                if are_programs_different(old_program, new_program):
                    logger.info(
                        f"Process group {new_program.name} has changed. Reloading process group..."
                    )
                    old_program.stop()
                    updated_program_list.append(new_program)
                    new_program.start()
                    logger.info(f"Process group {new_program.name} reloaded")
                # old process group without changes
                else:
                    logger.info(f"Process group {new_program.name} unchanged")
                    updated_program_list.append(old_program)
            # old process group that is no longer in config
            else:
                old_program.stop()
        # new process groups which where not in old process group list
        for new_program in new_program_list:
            updated_program: Program | None = find_process_in_list(
                new_program.name, updated_program_list
            )
            if not updated_program:
                logger.info(f"New Process group {new_program.name} to add")
                updated_program_list.append(new_program)
                new_program.start()

        logger.info("Config file reloaded successfully")
    except (TaskDefinitionError, ConfigError) as e:
        print(f"Error reloading config file: {e}")
    return updated_program_list


def show_status(programs: list[Program], return_string: str) -> str:
    for program in programs:
        return_string += f"{program.get_status()}\n"
        print(return_string)
    return return_string
