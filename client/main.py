import asyncio
import logging
from arg_parser import parse_server_port
from aioconsole import ainput, aprint

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


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
    try:
        while should_run['connection_active']:
            user_input_task = asyncio.create_task(ainput("> "))
            monitor_task = asyncio.create_task(monitor_state(should_run))

            done, pending = await asyncio.wait(
                [user_input_task, monitor_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()

            if not should_run['connection_active']:
                logger.info("\nExiting due to server shutdown or command termination.")
                break

            if user_input_task in done:
                command = user_input_task.result()
                if command == '':
                    logger.info("EOF received. Closing connection...")
                    should_run['connection_active'] = False
                    break

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
    except EOFError as e:
        logger.info("EOF received. Closing connection...")
        should_run['connection_active'] = False
    except Exception as e:
        logger.error(f"Error while sending user commands: {e.__class__.__name__}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def start_client(host, port):
    should_run = {'connection_active': True, 'waiting_for_response': False}
    reader, writer = None, None

    try:
        reader, writer = await asyncio.open_connection(host, port)
        logger.info("Connected to the server. Type 'exit' to exit.")

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
