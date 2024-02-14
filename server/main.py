import asyncio
import logging
import pathlib
from config_parser import (
    config_file_parser,
    parse_arguments,
    define_process_groups,
)
import argparse
from process_group import ProcessGroup
from functools import partial

logger = logging.getLogger("taskmaster")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


async def launch_taskmaster(
    args: argparse.Namespace, process_groups: list[ProcessGroup]
):
    config = config_file_parser(pathlib.Path(args.configuration_file_path))
    await define_process_groups(config, process_groups)
    # create a task group per task and a task per process in the task group


async def handle_command(command: str):
    cmds = command.split()
    match cmds[0]:
        case "start":
            return "Starting task"
        case "stop":
            return "Stopping task"
        case "restart":
            return "Restarting task"
        case "status":
            return "Showing status"
        case "reload":
            return "Reloading config"
        case "shutdown":
            return "Shutting down"
        case _:
            return "Invalid command"


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    process_groups: list[ProcessGroup],
):
    print("Client connected")
    while True:
        data = await reader.read(100)
        if not data:
            break
        message = data.decode()
        print(f"Received: {message}")
        response = await handle_command(message)
        if response:
            writer.write(response.encode())
            await writer.drain()
    print("Client disconnected")
    writer.close()
    await writer.wait_closed()


async def main():
    args = parse_arguments()
    port: int = args.server_port
    process_groups: list[ProcessGroup] = []

    server = await asyncio.start_server(
        partial(handle_client, process_groups=process_groups),
        "127.0.0.1",
        port,
    )
    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr}")

    taskmaster = asyncio.create_task(launch_taskmaster(args, process_groups))

    async with server:
        await asyncio.gather(server.serve_forever(), taskmaster)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Server stopped manually")
