import logging

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def command_interpreter(command: str):
	match command:
		case "start":
			logger.info("starting ...")
		case "stop":
			logger.info("stoping ...")
		case "restart":
			logger.info("restart")
		case _:
			logger.info("Unknown command: " + command)
			logger.info("Available commands: start, stop, restart")

def prompt_actions():
	while True:
		command = input(">>> ")
		command_interpreter(command)
	