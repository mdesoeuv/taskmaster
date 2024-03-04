import logging
from typing import Dict
from program import Program
from definitions import ProgramDefinition
from dataclasses import dataclass
from config_parser import (
    config_file_parser,
    TaskDefinitionError,
    ConfigError,
    define_programs,
)
from exceptions import ProcessException
from taskmaster import TaskMaster

logger = logging.getLogger(__name__)


def find_process_in_list(program_name: str, program_list: list[Program]):
    for process in program_list:
        if process.name == program_name:
            return process
    return None


async def exit_action(programs: Dict[str, Program]):
    logger.info("Exiting all processes...")
    # await asyncio.gather(*[program.stop() for program in programs.values()])
    for program in programs.values():
        program.kill()


@dataclass
class ProgramUpdate:
    program: Program
    definition: ProgramDefinition


async def reload_config_file(taskmaster: TaskMaster) -> str:
    logger.info("Reloading config file...")
    programs_to_add: Dict[str, ProgramDefinition] = {}
    updated_programs: Dict[str, Program] = {}
    try:
        new_config = config_file_parser(taskmaster.config_file)
        new_programs_definition = await define_programs(new_config)
        for old_program_name, old_program in taskmaster.programs.items():
            # old process group that is no longer in config
            if old_program_name not in new_programs_definition.keys():
                logger.debug(
                    f"Process group {old_program_name} is no longer in config, killing Program..."
                )
                old_program.kill()
            else:
                logger.debug(
                    f"Process group {old_program_name} is still in config, updating..."
                )
                # compare old and new programs
                old_program.update(new_programs_definition[old_program_name])
                updated_programs[old_program_name] = old_program

        # new process groups which where not in old process group list
        for (
            new_program_name,
            new_program_definition,
        ) in new_programs_definition.items():
            if new_program_name not in taskmaster.programs:
                logger.debug(
                    f"Process group {new_program_name} is new, adding Program..."
                )
                programs_to_add[new_program_name] = new_program_definition

        # add new programs
        updated_programs: Dict[str, Program] = await launch_programs(
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


async def shutdown(taskmaster: TaskMaster):
    print("\nShutting down server...")

    # Close all active client connections and prevent
    connections = list(taskmaster.active_connections.keys())
    shutdown_message = "server_shutdown"
    for addr in connections:
        writer = taskmaster.active_connections[addr]
        if writer:
            writer.write(shutdown_message.encode())
            await writer.drain()  # Assurez-vous que le message est envoyé.
            writer.close()
            await writer.wait_closed()

    taskmaster.server.close()
    await taskmaster.server.wait_closed()
    print("Server is closed")
    await exit_action(taskmaster.programs)
