import asyncio
import logging
import pathlib
from config_parser import (
    config_file_parser,
    parse_arguments,
    define_programs,
)
from functools import partial
from command_handler import handle_command
from actions import launch_programs
from taskmaster import TaskMaster

logger = logging.getLogger("taskmaster")
logging.basicConfig()
logger.setLevel(logging.DEBUG)

taskmaster: TaskMaster


async def launch_taskmaster(taskmaster: TaskMaster):
    config = config_file_parser(taskmaster.config_file)
    taskmaster.programs_definition = define_programs(
        config, taskmaster.programs
    )
    launch_programs(taskmaster.programs_definition, taskmaster.programs)


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    taskmaster: TaskMaster,
):
    print("Client connected")
    while True:
        data = await reader.read(100)
        if not data:
            break
        message = data.decode()
        print(f"Received: {message}")
        response = await handle_command(
            message, taskmaster
        )
        if response:
            writer.write(response.encode())
            await writer.drain()
    print("Client disconnected")
    writer.close()
    await writer.wait_closed()


async def main():
    global taskmaster

    args = parse_arguments()
    port: int = args.server_port
    config_file = pathlib.Path(args.configuration_file_path)
    taskmaster = TaskMaster(config_file=config_file)

    server = await asyncio.start_server(
        partial(handle_client, taskmaster),
        "127.0.0.1",
        port,
    )
    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr}")

    taskmaster = asyncio.create_task(launch_taskmaster(taskmaster))

    async with server:
        await asyncio.gather(server.serve_forever(), taskmaster)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Server stopped manually")
