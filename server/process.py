import asyncio
import logging
from dataclasses import dataclass
from typing import List
from enums import AutoRestart, Status, Signal
from datetime import datetime

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


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
    starttime: int
    stoptime: int
    status: Status = Status.STOPPED
    process: asyncio.subprocess.Process = (
        None  # Adjusted to asyncio subprocess
    )
    stopsignal: Signal = Signal("TERM")
    returncode: int = None
    retries: int = 0
    started_at: int = 0
    stopped_at: int = 0

    async def start(self):

        try:
            self.status = Status.STARTING
            self.returncode = None
            self.stopped_at = 0
            # Adjusted to use asyncio's subprocess and properly handle stdout/stderr
            self.process = await asyncio.create_subprocess_exec(
                *self.cmd.split(),
                cwd=self.cwd,
                env=self.env,
                stdout=(
                    asyncio.subprocess.PIPE
                    if self.stdout == "PIPE"
                    else open(self.stdout, "w")
                ),
                stderr=(
                    asyncio.subprocess.PIPE
                    if self.stderr == "PIPE"
                    else open(self.stderr, "w")
                ),
            )
            self.started_at = datetime.now()
            logger.debug(
                f"Process {self.name}, pid {self.process.pid}, STARTING"
            )
            await asyncio.sleep(self.starttime)
            self.status = Status.RUNNING
            logger.debug(
                f"Process {self.name}, pid {self.process.pid}, RUNNING"
            )
            await self.monitor_process()
        except Exception as e:
            self.stopped_at = datetime.now()
            self.status = Status.FATAL
            logger.error(f"Error in start process function: {e}")
            self.retry()
        return f"Process {self.name} started successfully."

    async def monitor_process(self):
        # Wait for the process to finish asynchronously
        self.returncode = await self.process.wait()
        self.stopped_at = datetime.now()
        logger.debug(f"Process {self.name} exited with code {self.returncode}")
        if self.returncode not in self.exitcodes:
            logger.error(
                f"Process {self.name} exited with unexpected code {self.returncode}"
            )
            self.status = Status.FATAL
            if self.autorestart == AutoRestart.unexpected:
                self.retry()
        else:
            self.status = Status.EXITED
            if self.autorestart == AutoRestart.true:
                self.retry()

    def retry(self):
        if (
            self.autorestart == AutoRestart.false
            or self.retries >= self.startretries
        ):
            logger.error(f"Max retries reached for process {self.name}")
            return
        self.retries += 1
        logger.info(
            f"Retrying process {self.name} ({self.retries}/{self.startretries})"
        )
        asyncio.create_task(self.start())

    async def stop(self):
        logger.debug(
            f"Stopping process {self.name} with signal {self.stopsignal.signal}"
        )
        if self.process:
            self.process.send_signal(self.stopsignal.signal)
            self.status = Status.STOPPING
            try:
                await asyncio.wait_for(
                    self.process.wait(), timeout=self.stoptime
                )
                logger.info(f"Process {self.name} stopped")
                self.stopped_at = datetime.now()
                self.status = Status.STOPPED
            except asyncio.TimeoutError:
                self.kill()
        else:
            logger.info(f"Process {self.name} is already stopped")

    def kill(self):
        self.autorestart = AutoRestart.false
        print(f"Killing process {self.name}: {self.process}")
        if self.process:
            try:
                self.process.kill()
                self.stopped_at = datetime.now()
                self.status = Status.FATAL
                logger.info(f"Process {self.name} killed")
            except ProcessLookupError:
                logger.info(f"Process {self.name} is already exited")
        else:
            logger.info(f"Process {self.name} is already stopped")

    def reset(self):
        self.retries = 0

    def get_uptime(self) -> int:
        difference = self.stopped_at - self.started_at if self.stopped_at else datetime.now() - self.started_at
        return str(difference)
