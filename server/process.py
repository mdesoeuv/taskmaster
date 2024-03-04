import asyncio
import logging
from dataclasses import dataclass
from typing import List
from enums import AutoRestart, Status, Signal
from datetime import datetime
from definitions import ProgramDefinition
from mail import email_alert

logger = logging.getLogger(__name__)


@dataclass
class Process:
    name: str
    cmd: str
    cwd: str
    env: dict
    umask: int
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
    mail_alerting: bool = False

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
                umask=self.umask,
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
            asyncio.create_task(self.watch_successfull_start())
            await self.monitor_process()
        except Exception as e:
            self.stopped_at = datetime.now()
            self.status = Status.FATAL
            logger.error(f"Error starting process {self.name}: {e}")
            self.retry()
            return f"Error starting process {self.name}: {e}"
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
            if self.autorestart == AutoRestart.always:
                self.retry()

    def retry(self):
        if self.retries >= self.startretries:
            log_string = f"Max retries reached for process: {self.name}"
            if self.returncode not in self.exitcodes:
                self.status = Status.ABORTED
                if self.mail_alerting:
                    asyncio.create_task(email_alert(
                        f"Process {self.name} aborted",
                        f"Process {self.name} aborted after max retries ({self.retries})"
                        )
                    )
                log_string += f" after unexpected exit code ({self.returncode}): ABORTED."
            logger.info(log_string)
            return
        if self.autorestart == AutoRestart.never:
            logger.debug(f"AutoRestart set to 'never' for process {self.name}")
            return
        self.retries += 1
        logger.info(
            f"Retrying process {self.name} ({self.retries}/{self.startretries})"
        )
        asyncio.create_task(self.start())

    async def stop(self):
        logger.debug(
            f"Stopping process {self.name} with signal {self.stopsignal}"
        )
        if self.process:
            self.process.send_signal(self.stopsignal)
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
        self.autorestart = AutoRestart.never
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
        if not self.started_at:
            return 0
        difference = (
            self.stopped_at - self.started_at
            if self.stopped_at
            else datetime.now() - self.started_at
        )
        return str(difference)

    async def watch_successfull_start(self):
        await asyncio.sleep(self.starttime)
        if self.returncode is None:
            self.status = Status.RUNNING
            logger.debug(
                f"Process {self.name}, pid {self.process.pid}, RUNNING"
            )

    def update(self, program_definition: ProgramDefinition):
        keys = [
            "cmd",
            "cwd",
            "env",
            "umask",
            "stdout",
            "stderr",
            "autorestart",
            "exitcodes",
            "startretries",
            "starttime",
            "stoptime",
            "stopsignal",
        ]
        attributes = {
            key: program_definition.__dict__[key] for key in set(keys)
        }
        self.__dict__.update(attributes)
        logger.info(f"Process {self.name} updated")
        return f"Process {self.name} updated successfully"
