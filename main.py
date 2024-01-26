import logging
import pathlib
from exceptions import TaskException 
from config_parser import config_file_parser, parse_arguments
from shell import prompt

logger = logging.getLogger("taskmaster")
logging.basicConfig()
logger.setLevel(logging.DEBUG)

def main():
    args = parse_arguments()
    config_file_parser(pathlib.Path(args.configuration_file_path))
    prompt()

if __name__ == "__main__":
    try:
        main()
    except TaskException as e:
        logger.error(e)