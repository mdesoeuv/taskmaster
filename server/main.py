import asyncio
import logging
import pathlib
from config_parser import (
    config_file_parser,
    parse_arguments,
    define_process_groups,
)
from process_group import ProcessGroup
from functools import partial
from command_handler import handle_command

logger = logging.getLogger("taskmaster")
logging.basicConfig()
logger.setLevel(logging.DEBUG)

process_groups: list[ProcessGroup] = []
config_file_path: str = ""


async def launch_taskmaster(
    config_file_path: str, process_groups: list[ProcessGroup]
):
    config = config_file_parser(pathlib.Path(config_file_path))
    await define_process_groups(config, process_groups)
    # create a task group per task and a task per process in the task group


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    process_groups: list[ProcessGroup],
    config_file_path: str,
):
    print("Client connected")
    while True:
        data = await reader.read(100)
        if not data:
            break
        message = data.decode()
        print(f"Received: {message}")
        response = await handle_command(
            message, process_groups, config_file_path
        )
        if response:
            writer.write(response.encode())
            await writer.drain()
    print("Client disconnected")
    writer.close()
    await writer.wait_closed()


async def main():
    global process_groups
    global config_file_path

    args = parse_arguments()
    port: int = args.server_port
    config_file_path = args.configuration_file_path

    server = await asyncio.start_server(
        partial(
            handle_client,
            process_groups=process_groups,
            config_file_path=config_file_path,
        ),
        "127.0.0.1",
        port,
    )
    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr}")

    taskmaster = asyncio.create_task(
        launch_taskmaster(config_file_path, process_groups)
    )

    async with server:
        await asyncio.gather(server.serve_forever(), taskmaster)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Server stopped manually")
