import logging
from typing import Dict
from program import Program
import pathlib
from config_parser import (
    config_file_parser,
    TaskDefinitionError,
    ConfigError,
    define_programs,
)
from program_definition import ProgramDefinition
from exceptions import ProcessException
from server.taskmaster import TaskMaster

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


def compare_programs(
    model1: BaseModel, model2: BaseModel
) -> Dict[str, Dict[str, Any]]:
    differences = {}
    for field in model1.__fields__:
        value1, value2 = getattr(model1, field), getattr(model2, field)
        if value1 != value2:
            differences[field] = {"model1": value1, "model2": value2}
    return differences


def reload_config_file(taskmaster: TaskMaster) -> Dict[str, Program]:
    logger.info("Reloading config file...")
    updated_program_list = []
    try:
        new_config = config_file_parser(taskmaster.config_file)
        new_programs_definition = define_programs(new_config)
        differences = compare_programs(
            taskmaster.programs_definition, new_programs_definition
        )

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


def show_status(programs: Dict[str, Program], return_string: str) -> str:
    for program in programs.values():
        return_string += f"{program.get_status()}\n"
        print(return_string)
    return return_string


def launch_programs(
    program_definitions: Dict[str, ProgramDefinition],
    programs: Dict[str, Program],
) -> Dict[str, Program]:
    for program_name, program_definition in program_definitions.items():
        try:
            program = Program(
                name=program_definition.name,
                cmd=program_definition.cmd,
                numprocs=program_definition.numprocs,
                umask=program_definition.umask,
                workingdir=program_definition.workingdir,
                autostart=program_definition.autostart,
                autorestart=program_definition.autorestart,
                exitcodes=program_definition.exitcodes,
                startretries=program_definition.startretries,
                starttime=program_definition.starttime,
                stoptime=program_definition.stoptime,
                stopsignal=program_definition.stopsignal,
                stdout=program_definition.stdout,
                stderr=program_definition.stderr,
                env=program_definition.env,
            )
            programs[program_name] = program
            if program.autostart:
                program.start()
        except Exception as e:
            raise ProcessException(
                f"Error creating process {program_name}: {e}"
            )
    return programs
