import logging
import pathlib
from exceptions import TaskException
from config_parser import config_file_parser, parse_arguments, define_tasks
from prompt import prompt
import asyncio

logger = logging.getLogger("taskmaster")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


async def start_tasks(tasks):
    # Assuming tasks is a list of Process objects with an async start method
    await asyncio.gather(*[task.start() for task in tasks])


async def main():
    args = parse_arguments()
    config = config_file_parser(pathlib.Path(args.configuration_file_path))
    tasks = define_tasks(
        config
    )  # This should return a list of tasks prepared for starting

    # Start all tasks concurrently and wait for them to start
    await start_tasks(tasks)

    # If you have a prompt coroutine for interaction, ensure it's awaited here
    #await prompt(tasks, args.configuration_file_path)


if __name__ == "__main__":
    asyncio.run(main())
