import logging
import yaml
import pathlib
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class TaskException(Exception):
    def __init__(self, message):            
        super().__init__(message)


class ConfigError(TaskException):
    def __init__(self, message):            
        super().__init__(message)


logger = logging.getLogger("taskmaster")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def config_parser(path: pathlib.Path):
    if not path.exists() or path.is_dir():
        raise ConfigError("configuration file error.")
    with open(path) as file:
        config = yaml.load(file, Loader=Loader)
        logger.info(config)


def main():
    logger.info("Hello !")
    config_parser(path=pathlib.Path("config.yaml"))
    # raise TaskException("Error happening !")


if __name__ == "__main__":
    try:
        main()
    except TaskException as e:
        logger.error(e)