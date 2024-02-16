import logging
from typing import Dict
from program import Program
from dataclasses import dataclass
from config_parser import (
    config_file_parser,
    TaskDefinitionError,
    ConfigError,
    define_programs,
)
from program_definition import ProgramDefinition
from exceptions import ProcessException
from taskmaster import TaskMaster
from process import Process

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def find_process_in_list(program_name: str, program_list: list[Program]):
    for process in program_list:
        if process.name == program_name:
            return process
    return None


def exit_action(programs: Dict[str, Program]):
    logger.info("Exiting all processes...")
    for program in programs.values():
        program.stop()
    exit(0)


def compare_program_defintions(
    old_program: ProgramDefinition, new_program: ProgramDefinition
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
        old_attr = getattr(old_program, attr)
        new_attr = getattr(new_program, attr)

        if old_attr != new_attr:
            # todo fix verification of depth
            print(old_program.stopsignal.signal)
            print(new_program.stopsignal.signal)
            print(f"Attribute {attr} has changed")
            return True

    return False


@dataclass
class ProgramUpdate:
    program: Program
    definition: ProgramDefinition


async def reload_config_file(taskmaster: TaskMaster) -> str:
    logger.info("Reloading config file...")
    programs_to_update: Dict[str, ProgramUpdate] = {}
    programs_to_add: Dict[str, ProgramDefinition] = {}
    updated_programs: Dict[str, Program] = {}
    try:
        new_config = config_file_parser(taskmaster.config_file)
        new_programs_definition = await define_programs(new_config)
        for old_program_name, old_program in taskmaster.programs.items():
            # old process group that is no longer in config
            if old_program_name not in new_programs_definition.keys():
                old_program.kill()
            else:
                # compare old and new program
                differences = compare_program_defintions(
                    taskmaster.programs_definition[old_program_name],
                    new_programs_definition[old_program_name],
                )
                if differences:
                    logger.info(
                        f"Process group {old_program_name} has changed. Reloading process group..."
                    )
                    # TODO update only specific fields and do not kill if unnecessary
                    old_program.autorestart = False
                    old_program.kill()
                    programs_to_add[old_program_name] = (
                        new_programs_definition[old_program_name]
                    )
                else:
                    logger.info(f"Process group {old_program_name} unchanged")
                    updated_programs[old_program_name] = old_program

        # new process groups which where not in old process group list
        for (
            new_program_name,
            new_program_definition,
        ) in new_programs_definition.items():
            if new_program_name not in taskmaster.programs:
                programs_to_add[new_program_name] = new_program_definition

        # add new programs
        updated_programs: Dict[str, Program] = launch_programs(
            programs_to_add, updated_programs
        )

        # update changed programs
        taskmaster.programs = updated_programs
        taskmaster.programs_definition = new_programs_definition

        logger.info("Config file reloaded successfully")
    except (TaskDefinitionError, ConfigError) as e:
        print(f"Error reloading config file: {e}")
        return f"Error reloading config file: {e}"
    return "Reloaded config file successfully"


def show_status(programs: Dict[str, Program], return_string: str) -> str:
    print("Showing status...")
    for program in programs.values():
        return_string += f"{program.get_status()}\n"
    return return_string


async def launch_programs(
    program_definitions: Dict[str, ProgramDefinition],
    programs: Dict[str, Program],
) -> Dict[str, Program]:
    for program_name, program_definition in program_definitions.items():
        try:
            program = Program(program_definition)
            programs[program_name] = program
            if program.autostart:
                program.start()
        except Exception as e:
            raise ProcessException(
                f"Error creating process {program_name}: {e}"
            )
    return programs
