import asyncio
import logging
from arg_parser import parse_server_port
from aioconsole import ainput, aprint
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

valid_commands = ['exit', 'reload', 'status', 'command']
command_completer = WordCompleter(valid_commands, ignore_case=True)

def is_command_valid(input_command: str) -> bool:
    command = input_command.split()

    match len(command):
        case 0:
            return False
        case 1:
            if command[0] not in ["exit", "reload", "status"]:
                logger.info("Not enough arguments. Usage: command [task_name]")
                return False
            else:
                return True
        case 2:
            return True
        case _:
            logger.info("Too many arguments. Usage: command [task_name]")
            return False


async def display_loading(should_run: dict, timeout=5):
    start_time = asyncio.get_running_loop().time()
    counter = 0
    while (asyncio.get_running_loop().time() - start_time) < timeout and should_run['waiting_for_response']:
        await asyncio.sleep(0.1)
        counter += 1
        if counter % 10 == 0:
            await aprint("loading...")
    if should_run['waiting_for_response']:
        await aprint("No response from server. Please check your connection.")
    should_run['waiting_for_response'] = False


async def listen_from_server(reader, should_run: dict):
    try:
        while not reader.at_eof() and should_run['connection_active']:
            data = await reader.readline()
            message = data.decode('utf-8')
            if message:
                should_run['waiting_for_response'] = False
                if message.strip() == "server_shutdown":
                    should_run['connection_active'] = False
                    break
                await aprint(message, end='')
    except Exception as e:
        logger.error(f"Error while listening for server messages: {e}")


async def monitor_state(should_run: dict):
    while should_run['connection_active']:
        await asyncio.sleep(0.1)



async def send_user_commands(writer, should_run: dict):
    session = PromptSession(history=InMemoryHistory(), auto_suggest=AutoSuggestFromHistory(), completer=command_completer)

    try:
        while should_run['connection_active']:
            try:
                command = await session.prompt_async("> ")
            except (EOFError, KeyboardInterrupt):
                logger.info("Exiting due to user interruption or EOF.")
                should_run['connection_active'] = False
                break

            if not command.strip():
                logger.info("Empty command received. Please enter a valid command.")
                continue

            if is_command_valid(command):
                should_run['waiting_for_response'] = True
                writer.write(command.encode())
                await writer.drain()

                if command == "exit":
                    logger.info("Exiting...")
                    should_run['connection_active'] = False
                    break

                loading_task = asyncio.create_task(display_loading(should_run))
                await loading_task
    except Exception as e:
        logger.error(f"Error while sending user commands: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def start_client(host, port):
    should_run = {'connection_active': True, 'waiting_for_response': False}
    reader, writer = None, None

    try:
        reader, writer = await asyncio.open_connection(host, port)
        logger.info("Connected to the server. Type 'exit' to kill server.")

        listener_task = asyncio.create_task(listen_from_server(reader, should_run))
        user_input_task = asyncio.create_task(send_user_commands(writer, should_run))

        await asyncio.gather(listener_task, user_input_task)

    except ConnectionRefusedError:
        logger.error("Server is not running. Please start the server and try again.")
    except KeyboardInterrupt:
        logger.info("Client interrupted by user. Closing connection...")
        should_run['connection_active'] = False
        if writer is not None:
            writer.close()
            await writer.wait_closed()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if writer is not None:
            writer.close()
            await writer.wait_closed()


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = parse_server_port()

    try:
        asyncio.run(start_client(HOST, PORT))
    except KeyboardInterrupt:
        logger.info("Client interrupted by user. Closing connection...")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
