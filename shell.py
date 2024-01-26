import logging

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)
import signal


def command_interpreter(command: str):
	match command:
		case "start":
			logger.info("starting ...")
		case "stop":
			logger.info("stoping ...")
		case "restart":
			logger.info("restart")
		case "status":
			logger.info("status")
		case "reload":
			logger.info("reload")
		case "exit":
			logger.info("exit")
		case _:
			logger.info("Unknown command: " + command)
			logger.info("Available commands: start, stop, restart, reload, status, exit")

def sigint_handler(signum, frame):
	logger.info("\nSIGINT received, stopping...")
	exit(0)


def prompt_actions():
	signal.signal(signal.SIGINT, sigint_handler)

	while True:
		command = input(">>> ")
		command_interpreter(command)
	