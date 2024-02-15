import asyncio
import logging
from dataclasses import dataclass
from typing import List
from helper import AutoRestart, Status, Signal

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
    stopflag: bool = False

    async def start(self):
        if self.stopflag:
            return
        try:
            self.status = Status.STARTING
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
            self.status = Status.FATAL
            logger.error(f"Error in start process function: {e}")
            self.retry()

    async def monitor_process(self):
        # Wait for the process to finish asynchronously
        self.returncode = await self.process.wait()
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

    async def kill(self):
        self.stopflag = True
        logger.debug(f"Stopping process {self.name} with signal {self.stopsignal.signal}")
        if self.process and self.process.returncode is None:
            self.process.send_signal(self.stopsignal.signal)
            self.status = Status.STOPPING
            try:
                await asyncio.wait_for(self.process.wait(), timeout=self.stoptime)
                logger.info(f"Process {self.name} stopped")
                self.status = Status.STOPPED
            except asyncio.TimeoutError:
                self.process.kill()
                self.status = Status.FATAL
                logger.info(f"Process {self.name} killed")
        else:
            logger.info(f"Process {self.name} is already stopped")
