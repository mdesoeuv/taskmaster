import logging
import argparse
import yaml
import pathlib
from exceptions import ConfigError
from typing import Dict
from enums import Signal, AutoRestart
from exceptions import ProgramDefinitionError
from definitions import ProgramDefinition

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

logger = logging.getLogger(__name__)


def config_file_parser(path: pathlib.Path) -> Dict:
    if not path.exists() or path.is_dir():
        raise ConfigError(
            "The configuration `"
            + str(path)
            + "` file does not exist or is a directory."
        )
    with open(path) as file:
        config = yaml.load(file, Loader=Loader)
        logger.info("Configuration file parsed successfully.")
    return config


def format_env(env: dict) -> dict:
    formatted = {}
    for key, value in env.items():
        formatted[key] = str(value)
    return formatted


async def define_programs(
    config: dict,
) -> Dict[str, ProgramDefinition]:
    logger.debug("defining programs...")
    programs_definition: Dict[str, ProgramDefinition] = {}
    program_list = config["programs"].keys()
    for program_name in program_list:
        prog = config["programs"][program_name]
        try:
            program = ProgramDefinition(
                name=program_name,
                cmd=prog.get("cmd"),
                numprocs=prog.get("numprocs", 1),
                umask=int(prog.get("umask", "022"), 8),
                cwd=prog.get("workingdir", "."),
                autostart=prog.get("autostart", True),
                autorestart=AutoRestart(
                    str(prog.get("autorestart", "unexpected")).lower()
                ),
                exitcodes=prog.get("exitcodes", [0]),
                startretries=prog.get("startretries", 3),
                starttime=prog.get("starttime", 0),
                stopsignal=Signal(prog.get("stopsignal", "TERM")).signal,
                stoptime=prog.get("stoptime", 10),
                stdout=prog.get("stdout", "/dev/null"),
                stderr=prog.get("stderr", "/dev/null"),
                env=format_env(prog.get("env", {})),
                mail_alerting=prog.get("mail_alerting", False),
            )
        except Exception as e:
            logger.error("Error while parsing task definition.")
            raise ProgramDefinitionError(
                "Error while parsing task definition. "
                "Check the configuration file: " + str(e)
            )
        programs_definition[program_name] = program
        if len(programs_definition) == 0:
            raise ProgramDefinitionError(
                "No program defined in the configuration file."
            )
    return programs_definition


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process taskmaster options.")
    parser.add_argument(
        "-c",
        dest="configuration_file_path",
        type=str,
        required=True,
        help="Specify the path of the configuration file.",
    )
    parser.add_argument(
        "-p",
        dest="server_port",
        type=str,
        required=True,
        help="Specify the port to use for the server.",
    )
    args = parser.parse_args()
    return args
