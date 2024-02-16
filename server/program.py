import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict
from yamldataclassconfig.config import YamlDataClassConfig
from exceptions import ProcessException
from process import Process
from enums import Status
from program_definition import ProgramDefinition

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


@dataclass
class Program(ProgramDefinition):
    processes: Dict[int, "Process"] = field(default_factory=dict)

    def __init__(self, program_definition: ProgramDefinition):
        # Init the ProgramDefinition attributes coming from herited class
        super().__init__(**program_definition.__dict__)
        # Init the Program attributes
        self.processes = {}

    def start(self):
        logger.info(f"Starting task {self.name}")
        errors = 0
        try:
            for process_id in range(self.numprocs):
                try:
                    self.processes[process_id] = Process(
                        name=f"{self.name}-{process_id}",
                        cmd=self.cmd,
                        cwd=self.workingdir,
                        env=self.env,
                        umask=self.umask,
                        stdout=self.stdout,
                        stderr=self.stderr,
                        exitcodes=self.exitcodes,
                        stopsignal=self.stopsignal,
                        starttime=self.starttime,
                        stoptime=self.stoptime,
                        autorestart=self.autorestart,
                        startretries=self.startretries,
                    )
                    logger.debug(f"Starting process {self.name}-{process_id}")
                    asyncio.create_task(self.processes[process_id].start())
                    logger.debug(f"Process {self.name}-{process_id} started")
                except Exception as e:
                    raise ProcessException(
                        f"Error starting process {self.name}-{process_id}: {e}"
                    )
                logger.debug(
                    f"Task {self.name}: {process_id + 1}/{self.numprocs} started successfully"
                )

        except Exception as e:
            logger.error(f"Error starting Program: {e}")
            errors += 1
            return f"Error starting Program {self.name}: {self.numprocs - errors}/{self.numprocs} started successfully"
        logger.debug(f"Task {self.name} started successfully")
        return f"Task {self.name} started successfully"

    async def stop(self):
        logger.info(f"Stopping task {self.name}")
        try:
            # Wait for process to stop
            for process_id in range(self.numprocs):
                if not self.processes or not self.processes[process_id]:
                    logger.debug(
                        f"Process {self.name}-{process_id} is already stopped"
                    )
                    continue
                logger.debug(f"Stopping process {self.name}-{process_id}")
                await self.processes[process_id].stop()

        except Exception as e:
            logger.error(f"Error stopping process: {e}")
            return f"Error stopping task {self.name}: {e}"
        logger.info(f"Task {self.name} stopped successfully")
        return f"Task {self.name} stopped successfully"

    def restart(self):

        self.kill()
        for process in self.processes.values():
            process.reset()
        self.start()
        return "Program restarted"

    def kill(self):
        for process in self.processes.values():
            process.kill()
        return "Program killed"

    def get_status(self) -> str:
        print("Getting status")
        for process_id in range(self.numprocs):
            if (
                self.processes.get(process_id)
                and self.processes[process_id].process
            ):
                pid = self.processes[process_id].process.pid
                status = self.processes[process_id].status
                returncode = self.processes[process_id].returncode
                return f"{self.name}-{process_id}: {status} ({returncode}), pid {pid}, uptime "  # {get_process_uptime(pid)}"
            else:
                return f"{self.name}-{process_id}: STOPPED"
