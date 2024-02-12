from dataclasses import dataclass, field
import logging
import subprocess
import time
from typing import List, Dict
from enum import Enum
from yamldataclassconfig.config import YamlDataClassConfig

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


class Signal(Enum):
    TERM = "TERM"
    HUP = "HUP"
    INT = "INT"
    QUIT = "QUIT"
    KILL = "KILL"


class Status(Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    EXITED = "EXITED"
    FATAL = "FATAL"


@dataclass
class Task(YamlDataClassConfig):
    name: str
    cmd: str
    numprocs: int = 1
    umask: str = "022"
    workingdir: str = "/tmp"
    autostart: bool = True
    autorestart: bool = True
    exitcodes: List[int] = field(default_factory=lambda: [0, 1])
    startretries: int = 3
    starttime: int = 0
    stopsignal: Signal = Signal.TERM
    stoptime: int = 10
    stdout: str = "/dev/null"
    stderr: str = "/dev/null"
    env: dict = None
    process: Dict[int, subprocess.Popen] = field(init=False, default=None)
    status: Dict[int, Status] = field(
        init=False, default_factory=lambda: {0: Status.STOPPED}
    )
    retries: int = 0

    def start(self):
        logger.info(f"Starting task {self.name}")
        if self.process:
            logger.info(f"Task {self.name} is already running")
            return
        errors = 0
        for process_id in range(self.numprocs):
            try:
                # print(self)
                # Environment variables setup todo

                # Wait for the process to start successfully
                time.sleep(self.starttime)

                logger.info(f"Starting process {self.name}-{process_id}")

                # Start the process
                self.process[process_id] = subprocess.Popen(
                    self.cmd.split(),
                    shell=False,
                    text=True,
                    stdout=open(self.stdout, "w"),
                    stderr=open(self.stderr, "w"),
                    cwd=self.workingdir,
                    env=self.env,
                    postexec_fn=execution_callback(self),
                    name=f"{self.name}-{process_id}",
                )
                self.status[process_id] = Status.RUNNING
            except Exception as e:
                # Handle errors in process starting
                logger.error(f"Error starting process: {e}")
                errors += 1
        logger.info(
            f"Task {self.name}: {self.numprocs - errors}/{self.numprocs} started successfully"
        )

    def stop(self):
        logger.info(f"Stopping task {self.name}")
        for process_id in range(self.numprocs):
            if (
                not self.process
                or not self.process[process_id]
                or not self.process[process_id].poll()
            ):
                logger.info(f"Process {self.name} is already stopped")
                self.process = None
                return
            try:
                # Wait for process to stop
                start_time = time.time()
                while time.time() - start_time < self.stoptime:
                    if self.process is not None:
                        return  # Process stopped gracefully
                    time.sleep(0.5)
                # Force kill the process
                self.process.kill()
            except Exception as e:
                logger.error(f"Error stopping process: {e}")
        logger.info(f"Task {self.name} stopped successfully")

    def restart(self):
        self.stop()
        self.start()

    def get_status(self):
        print(f"{self.name: }")


def execution_callback(task: Task):
    logger.info(f"{task.name}: Stopped")
