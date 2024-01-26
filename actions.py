import logging

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def start():
    logger.info("starting ...")


def stop():
    logger.info("stoping ...")


def restart():
    logger.info("restart")


def status():
    logger.info("status")


def reload():
    logger.info("reload")


def exit_action():
    logger.info("exiting ...")
