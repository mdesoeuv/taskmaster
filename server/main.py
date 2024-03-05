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
from actions import launch_programs, reload_config_file, shutdown
from taskmaster import TaskMaster


try:
    logger = logging.getLogger()
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)-8s: %(name)-8s: %(message)-8s"
    )
    file_handler = logging.FileHandler("./logs/taskmaster.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
except Exception as e:
    logging.error(f"Logger configuration error: {e}")
    exit(1)


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
    logger.info(f"Client {addr} connected")
    taskmaster.active_connections[addr] = writer

    try:
        while True:
            data = await reader.read(100)
            if not data:
                break
            message = data.decode()
            logger.debug(f"Received: {message}")
            response = await handle_command(message, taskmaster, logger)
            if response:
                # if response does not end with \n, add it
                if not response.endswith("\n"):
                    response = response + "\n"
                logger.debug(f"Sending: {response}")
                writer.write(response.encode())
                await writer.drain()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info(f"Client {addr} disconnected")
        writer.close()
        await writer.wait_closed()
        taskmaster.active_connections.pop(addr)


async def main():
    loop = asyncio.get_running_loop()

    args = parse_arguments()
    port: int = args.server_port
    config_file = pathlib.Path(args.configuration_file_path)
    taskmaster: TaskMaster = TaskMaster(config_file=config_file)

    taskmaster.server = await asyncio.start_server(
        partial(handle_client, taskmaster=taskmaster),
        "127.0.0.1",
        port,
    )
    addr = taskmaster.server.sockets[0].getsockname()
    logger.info(f"Server listening on {addr}")

    taskmaster_task = asyncio.create_task(launch_taskmaster(taskmaster))

    for signame in ("SIGINT", "SIGTERM"):
        loop.add_signal_handler(
            getattr(signal, signame),
            lambda: asyncio.create_task(shutdown(taskmaster)),
        )

    loop.add_signal_handler(
        signal.SIGHUP,
        lambda: asyncio.create_task(reload_config_file(taskmaster)),
    )

    async with taskmaster.server:
        try:
            await asyncio.gather(
                taskmaster.server.serve_forever(), taskmaster_task
            )
        except asyncio.CancelledError:
            # This exception is expected during shutdown, so you can ignore it
            logger.info("Server tasks cancelled as part of shutdown process.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")


try:
    asyncio.run(main())
except KeyboardInterrupt:
    logger.info("Server stopped manually")
