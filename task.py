from dataclasses import dataclass, field
import os
import logging
import subprocess
import time
import signal
from typing import List, Dict
from enum import Enum
from yamldataclassconfig.config import YamlDataClassConfig
from threading import Thread


logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


SIGNAL_MAP = {
    "TERM": signal.SIGTERM,
    "HUP": signal.SIGHUP,
    "INT": signal.SIGINT,
    "QUIT": signal.SIGQUIT,
    "KILL": signal.SIGKILL,
    "USR1": signal.SIGUSR1,
    "USR2": signal.SIGUSR2,
}


class Signal:
    def __init__(self, sig: str = "TERM"):
        self.signal = SIGNAL_MAP[sig]


class Status(str, Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    EXITED = "EXITED"
    FATAL = "FATAL"

    def __str__(self) -> str:
        return self.value


class AutoRestart(str, Enum):
    unexpected = "unexpected"
    true = "true"
    false = "false"

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
    autorestart: AutoRestart
    exitcodes: List[int]
    startretries: int
    status: Status = Status.STOPPED
    process: subprocess.CompletedProcess = None
    stopsignal: Signal = Signal("TERM")
    returncode: int = None
    retries: int = 0
    pid: int = None
    starttime: int = 0
    stoptime: int = 0
    stopflag: bool = False

    def start(self):
        if self.stopflag:
            return
        try:
            time.sleep(self.starttime)
            self.process = subprocess.Popen(
                self.cmd.split(),
                shell=False,
                text=True,
                stdout=open(self.stdout, "w"),
                stderr=open(self.stderr, "w"),
                cwd=self.cwd,
                umask=self.umask,
                env=self.env,
            )
            self.pid = self.process.pid
            self.status = Status.RUNNING
            self.process.wait()
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
                if self.autorestart != AutoRestart.false:
                    self.retry()
        except Exception as e:
            self.status = Status.FATAL
            logger.error(f"Error starting process: {e}")
            self.retry()

    def retry(self):
        if self.autorestart == AutoRestart.false:
            return
        if self.retries < self.startretries:
            self.retries += 1
            logger.info(
                f"Retrying process {self.name} ({self.retries}/{self.startretries})"
            )
            self.start()
        else:
            logger.error(f"Max retries reached for process {self.name}")
            self.status = Status.FATAL

    def kill(self):

        self.stopflag = True

        # poll() returns None if the process is still running
        if self.process and self.process.poll() is None:
            start_time = time.time()
            while time.time() - start_time < self.stoptime:
                time.sleep(0.5)
            os.kill(self.process.pid, self.stopsignal.signal)
            self.status = Status.STOPPED
            logger.info(f"Process {self.name} killed")
        else:
            logger.info(f"Process {self.name} is already stopped")

    def __str__(self):
        if self.process:
            return f"{self.name}: {self.status} pid {self.process.pid} ({self.returncode})"
        else:
            return f"{self.name}: {self.status}"


@dataclass
class Task(YamlDataClassConfig):
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
    process: Dict[int, Process] = field(init=False, default_factory=dict)
    status: Dict[int, Status] = field(init=False)
    threads: Dict[int, Thread] = field(init=False)

    def __post_init__(self):
        self.status = {i: Status.STOPPED for i in range(self.numprocs)}
        self.threads = {i: None for i in range(self.numprocs)}
        if self.autostart:
            self.start()

    def start(self):
        logger.info(f"Starting task {self.name}")
        errors = 0
        for process_id in range(self.numprocs):
            try:
                # Wait for the process to start successfully
                logger.debug(f"Starting process {self.name}-{process_id}")

                self.process[process_id] = Process(
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
                    startretries=self.startretries
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
                    logger.debug(
                        f"Process {self.name}-{process_id} is already stopped"
                    )
                    continue
                logger.debug(f"Stopping process {self.name}-{process_id}")
                self.process[process_id].kill()
                self.threads[process_id].join(timeout=0.5)

        except Exception as e:
            logger.error(f"Error stopping process: {e}")
        logger.info(f"Task {self.name} stopped successfully")

    def restart(self):
        self.stop()
        self.start()

    def get_status(self):
        for process_id in range(self.numprocs):
            if self.process[process_id]:
                print(f"Repr: {self.process[process_id]}")
            else:
                print(f"{self.name}-{process_id}: UNKNOWN")
