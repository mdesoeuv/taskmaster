import logging
from exceptions import TaskException 
from config_parser import parse_args_and_config
from shell import prompt_actions

logger = logging.getLogger("taskmaster")
logging.basicConfig()
logger.setLevel(logging.DEBUG)

def main():
    logger.info("Hello !")   
    parse_args_and_config() 
    prompt_actions()

if __name__ == "__main__":
    try:
        main()
    except TaskException as e:
        logger.error(e)