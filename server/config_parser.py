import logging
import argparse
import yaml
import pathlib
from exceptions import ConfigError
from typing import List
from enums import Signal, AutoRestart
from exceptions import TaskDefinitionError
from program import Program

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def config_file_parser(path: pathlib.Path) -> List[Program]:
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


async def define_programs(config: dict, programs: List[Program]):
    program_list = config["programs"].keys()
    for program in program_list:
        prog = config["programs"][program]
        try:
            program = Program(
                name=program,
                cmd=prog.get("cmd"),
                numprocs=prog.get("numprocs"),
                umask=prog.get("umask"),
                workingdir=prog.get("workingdir"),
                autostart=prog.get("autostart"),
                autorestart=AutoRestart(str(prog.get("autorestart")).lower()),
                exitcodes=prog.get("exitcodes"),
                startretries=prog.get("startretries"),
                starttime=prog.get("starttime"),
                stopsignal=Signal(prog.get("stopsignal")),
                stoptime=prog.get("stoptime"),
                stdout=prog.get("stdout"),
                stderr=prog.get("stderr"),
                env=format_env(prog.get("env", {})),
            )
            if program.autostart:
                await program.start()
        except Exception as e:
            logger.error("Error while parsing task definition.")
            raise TaskDefinitionError(
                "Error while parsing task definition. "
                "Check the configuration file: " + str(e)
            )
        programs.append(program)
        if len(programs) == 0:
            raise TaskDefinitionError(
                "No task defined in the configuration file."
            )
    return programs


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
