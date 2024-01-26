import logging
import yaml
import pathlib
from exceptions import TaskException, ConfigError 
from cli import parse_arguments
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

logger = logging.getLogger("taskmaster")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def config_parser(path: pathlib.Path):
    if not path.exists() or path.is_dir():
        raise ConfigError("The configuration `" + str(path) + "` file does not exist or is a directory.")
    with open(path) as file:
        config = yaml.load(file, Loader=Loader)
        logger.info(config)


def main():
    logger.info("Hello !")
    args = parse_arguments()
    config_parser(path=pathlib.Path(args.configuration_file_path))

if __name__ == "__main__":
    try:
        main()
    except TaskException as e:
        logger.error(e)