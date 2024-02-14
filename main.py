import logging
import pathlib
from server.exceptions import TaskException
from server.config_parser import config_file_parser, parse_arguments, define_tasks
from prompt import prompt

logger = logging.getLogger("taskmaster")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def main():
    args = parse_arguments()
    config = config_file_parser(pathlib.Path(args.configuration_file_path))
    tasks = define_tasks(config)
    prompt(tasks, args.configuration_file_path)


if __name__ == "__main__":
    try:
        main()
    except TaskException as e:
        logger.error(f"Error: {e}")
