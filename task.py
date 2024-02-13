from dataclasses import dataclass, field
import logging
import subprocess
import time
from typing import List, Dict
from enum import Enum
from yamldataclassconfig.config import YamlDataClassConfig
from threading import Thread

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


class Signal(str, Enum):
    TERM = "TERM"
    HUP = "HUP"
    INT = "INT"
    QUIT = "QUIT"
    KILL = "KILL"


class Status(str, Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    EXITED = "EXITED"
    FATAL = "FATAL"

    def __str__(self) -> str:
        return self.value


@dataclass
class Process:
    name: str
    cmd: str
    cwd: str
    env: dict
    umask: str
    stdout: str
    stderr: str
    exitcodes: List[int]
    status: Status = Status.STOPPED
    process: subprocess.CompletedProcess = None
    returncode: int = None
    retries: int = 0
    max_retries: int = 3

    def start(self):
        self.status = Status.RUNNING
        try:
            self.process = subprocess.run(
                self.cmd.split(),
                shell=False,
                text=True,
                stdout=open(self.stdout, "w"),
                stderr=open(self.stderr, "w"),
                cwd=self.cwd,
                umask=self.umask,
                env=self.env,
            )
            self.returncode = self.process.returncode
            self.status = Status.EXITED
            logger.debug(
                f"Process {self.name} exited with code {self.returncode}"
            )
            if self.returncode not in self.exitcodes:
                logger.error(
                    f"Process {self.name} exited with unexepected code {self.returncode} not in {self.exitcodes}"
                )
                self.status = Status.FATAL
                self.retry()
        except Exception as e:
            self.status = Status.FATAL
            logger.error(f"Error starting process: {e}")
            self.retry()

    # def stop(self):
    #     if self.process:
    #         self.process.terminate()
    #         self.status = Status.STOPPED
    #         logger.info(f"Process {self.name} stopped")
    #     else:
    #         logger.info(f"Process {self.name} is already stopped")

    def retry(self):
        if self.retries < self.max_retries:
            self.retries += 1
            logger.info(
                f"Retrying process {self.name} ({self.retries}/{self.max_retries})"
            )
            self.start()
        else:
            logger.error(f"Max retries reached for process {self.name}")
            self.status = Status.FATAL

    def kill(self):
        if self.process:
            self.process.kill()
            self.status = Status.STOPPED
            logger.info(f"Process {self.name} killed")
        else:
            logger.info(f"Process {self.name} is already stopped")

    def __str__(self):
        return f"{self.name}: {self.status} pid {self.process.pid} ({self.returncode})"


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
    process: Dict[int, Process] = field(init=False, default_factory=dict)
    retries: int = 0
    status: Dict[int, Status] = field(init=False)
    threads: Dict[int, Thread] = field(init=False)

    def __post_init__(self):
        self.status = {i: Status.STOPPED for i in range(self.numprocs)}
        self.threads = {i: None for i in range(self.numprocs)}

    def start(self):
        logger.info(f"Starting task {self.name}")
        errors = 0
        for process_id in range(self.numprocs):
            try:
                # Wait for the process to start successfully
                logger.debug(f"Starting process {self.name}-{process_id}")
                time.sleep(self.starttime)

                self.process[process_id] = Process(
                    name=f"{self.name}-{process_id}",
                    cmd=self.cmd,
                    cwd=self.workingdir,
                    env=self.env,
                    umask=self.umask,
                    stdout=self.stdout,
                    stderr=self.stderr,
                    exitcodes=self.exitcodes,
                )
                # Start the process
                self.threads[process_id] = Thread(
                    target=self.process[process_id].start, args=()
                )
                self.threads[process_id].start()
            except Exception as e:
                # Handle errors in process starting
                logger.error(f"Error starting process: {e}")
                errors += 1
                self.status[process_id] = Status.FATAL
        logger.info(
            f"Task {self.name}: {self.numprocs - errors}/{self.numprocs} started successfully"
        )

    def stop(self):
        logger.info(f"Stopping task {self.name}")
        try:
            # Wait for process to stop
            for process_id in range(self.numprocs):
                if not self.process or not self.process[process_id]:
                    logger.info(
                        f"Process {self.name}-{process_id} is already stopped"
                    )
                    self.status[process_id] = Status.STOPPED
                    continue
                logger.debug(f"Stopping process {self.name}-{process_id}")
                start_time = time.time()
                while time.time() - start_time < self.stoptime:
                    if self.process[process_id] is not None:
                        self.threads[process_id].join(timeout=0.5)
                        self.status[process_id] = Status.STOPPED
                        self.process[process_id] = None
                        break
                    time.sleep(0.5)
            self.process = None

        except Exception as e:
            logger.error(f"Error stopping process: {e}")
        logger.info(f"Task {self.name} stopped successfully")

    def restart(self):
        self.stop()
        self.start()

    def get_status(self):
        for process_id in range(self.numprocs):
            print(
                f"{self.name}-{process_id}: {self.process[process_id].status}"
            )


def execution_callback(task: Task):
    logger.info(f"{task.name}: Stopped")
