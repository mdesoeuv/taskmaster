import asyncio
import logging
import pathlib
from config_parser import config_file_parser, parse_arguments, define_tasks
import argparse

logger = logging.getLogger("taskmaster")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


async def manage_tasks(args: argparse.Namespace):
    config = config_file_parser(pathlib.Path(args.configuration_file_path))
    print(config)
    tasks = define_tasks(config)


async def handle_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
):
    print("Client connected")
    while True:
        data = await reader.read(100)
        if not data:
            break
        message = data.decode()
        print(f"Received {message}")
        # Logic to handle the message
        writer.write(data)
        await writer.drain()
    print("Client disconnected")
    writer.close()
    await writer.wait_closed()


async def main():
    args = parse_arguments()
    port: int = args.server_port
    server = await asyncio.start_server(
        handle_client, "127.0.0.1", port
    )
    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr}")

    task = asyncio.create_task(manage_tasks(args))

    async with server:
        await asyncio.gather(server.serve_forever(), task)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Server stopped manually")
