import asyncio
import logging
import pathlib
import signal
from config_parser import (
    config_file_parser,
    parse_arguments,
    define_programs,
)
from functools import partial
from command_handler import handle_command
from actions import exit_action, launch_programs
from taskmaster import TaskMaster

logger = logging.getLogger("taskmaster")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


async def launch_taskmaster(taskmaster: TaskMaster):
    config = config_file_parser(taskmaster.config_file)
    taskmaster.programs_definition = await define_programs(config)
    await launch_programs(taskmaster.programs_definition, taskmaster.programs)


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    taskmaster: TaskMaster,
):
    addr = writer.get_extra_info("peername")
    print(f"Client {addr} connected")
    taskmaster.active_connections[addr] = writer

    print("Client connected")
    try:
        while True:
            data = await reader.read(100)
            if not data:
                break
            message = data.decode()
            print(f"Received: {message}")
            response = await handle_command(message, taskmaster)
            if response:
                print(f"Sending: {response}")
                writer.write(response.encode())
                await writer.drain()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print(f"Client {addr} disconnected")
        writer.close()
        await writer.wait_closed()
        taskmaster.active_connections.pop(addr)


async def shutdown(server: asyncio.Server, taskmaster: TaskMaster):
    print("\nShutting down server...")

    # Close all active client connections and prevent
    connections = list(taskmaster.active_connections.keys())
    shutdown_message = "server_shutdown"
    for addr in connections:
        writer = taskmaster.active_connections[addr]
        if writer:
            writer.write(shutdown_message.encode())
            await writer.drain()  # Assurez-vous que le message est envoyé.
            writer.close()
            await writer.wait_closed()

    server.close()
    await server.wait_closed()
    print("Server is closed")
    await exit_action(taskmaster.programs)


async def main():
    loop = asyncio.get_running_loop()

    args = parse_arguments()
    port: int = args.server_port
    config_file = pathlib.Path(args.configuration_file_path)
    taskmaster: TaskMaster = TaskMaster(config_file=config_file)

    server = await asyncio.start_server(
        partial(handle_client, taskmaster=taskmaster),
        "127.0.0.1",
        port,
    )
    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr}")

    taskmaster_task = asyncio.create_task(launch_taskmaster(taskmaster))

    for signame in ("SIGINT", "SIGTERM"):
        loop.add_signal_handler(
            getattr(signal, signame),
            lambda: asyncio.create_task(shutdown(server, taskmaster)),
        )

    async with server:
        try:
            await asyncio.gather(server.serve_forever(), taskmaster_task)
        except asyncio.CancelledError:
            # This exception is expected during shutdown, so you can ignore it
            logger.info("Server tasks cancelled as part of shutdown process.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Server stopped manually")
