import logging

class TaskException(Exception):
    def __init__(self, message):            
        super().__init__(message)


logger = logging.getLogger("taskmaster")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def main():
    logger.info("Hello !")
    raise TaskException("Error happening !")

if __name__ == "__main__":
    try:
        main()
    except TaskException as e:
        logger.error(e)