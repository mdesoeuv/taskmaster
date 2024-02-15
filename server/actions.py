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


def exit_action(programs: Dict[str, Program]):
    logger.info("Exiting all processes...")
    for program in programs.values():
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


@dataclass
class ProgramUpdate:
    program: Program
    definition: ProgramDefinition


def reload_config_file(taskmaster: TaskMaster) -> str:
    logger.info("Reloading config file...")
    programs_to_update: Dict[str, ProgramUpdate] = {}
    programs_to_add: Dict[str, ProgramDefinition] = {}
    updated_programs: Dict[str, Program] = {}

    try:
        new_config = config_file_parser(taskmaster.config_file)
        new_programs_definition = define_programs(new_config)

        for old_program_name, old_program in taskmaster.programs.items():
            # old process group that is no longer in config
            if old_program not in new_programs_definition:
                old_program.stop()
            else:
                # compare old and new program
                differences = compare_programs(
                    taskmaster.programs[old_program],
                    new_programs_definition[old_program],
                )
                if differences:
                    logger.info(
                        f"Process group {old_program} has changed. Reloading process group..."
                    )
                    programs_to_update[old_program_name] = ProgramUpdate(
                        program=old_program,
                        definition=new_programs_definition[old_program],
                    )
                else:
                    logger.info(f"Process group {old_program} unchanged")
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
