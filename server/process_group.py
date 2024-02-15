import asyncio
import logging
from dataclasses import dataclass, field
from typing import List, Dict
from yamldataclassconfig.config import YamlDataClassConfig
from exceptions import ProcessException
from process import Process
from enums import AutoRestart, Status, Signal
from tools import get_process_name, get_process_uptime

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


@dataclass
class ProcessGroup(YamlDataClassConfig):
    name: str
    cmd: str
    numprocs: int = 1
    umask: str = "022"
    workingdir: str = "/tmp"
    autostart: bool = True
    autorestart: AutoRestart = AutoRestart.unexpected
    exitcodes: List[int] = field(default_factory=lambda: [0, 1])
    startretries: int = 3
    starttime: int = 0
    stopsignal: Signal = Signal("TERM")
    stoptime: int = 10
    stdout: str = "/dev/null"
    stderr: str = "/dev/null"
    env: dict = None
    processes: Dict[int, Process] = field(init=False, default_factory=dict)
    status: Dict[int, Status] = field(init=False)

    def __post_init__(self):
        self.status = {i: Status.STOPPED for i in range(self.numprocs)}

    async def start(self):
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
                        stopflag=False,
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
                    f"Task {self.name}: {self.numprocs - errors}/{self.numprocs} started successfully"
                )

        except Exception as e:
            logger.error(f"Error starting processGroup: {e}")
            errors += 1
            self.status[process_id] = Status.FATAL
        # logger.info(
        #     f"Task {self.name}: {self.numprocs - errors}/{self.numprocs} started successfully"
        # )
        logger.debug(f"Task {self.name} started successfully")

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
                await self.processes[process_id].kill()

        except Exception as e:
            logger.error(f"Error stopping process: {e}")
        logger.info(f"Task {self.name} stopped successfully")

    def restart(self):
        self.stop()
        self.start()

    def get_status(self) -> str:
        print("Getting status")
        for process_id in range(self.numprocs):
            if self.processes.get(process_id):
                pid = self.processes[process_id].process.pid
                status = self.processes[process_id].status
                return f"{self.name}-{process_id}: {status} (pid {pid}), uptime "  # {get_process_uptime(pid)}"
            else:
                return f"{self.name}-{process_id}: STOPPED"
