import logging

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def command_interpreter(command: str):
	match command:
		case "start":
			print("starting ...")
		case "stop":
			print("stoping ...")
		case "restart":
			print("restart")
		case _:
			print("Unknown command: " + command)

def prompt_actions():
	while True:
        # Attendre une commande de l'utilisateur
		command = input(">>> ")
		command_interpreter(command)
	