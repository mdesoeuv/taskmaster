from dataclasses import dataclass, field
import logging
import signal
import subprocess
import time
from typing import List
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
    process: subprocess.Popen = field(init=False, default=None)

    def start(self):
        logger.info(f"Starting task {self.name}")
        if self.process:
            logger.info(f"Task {self.name} is already running")
            return
        try:
            print(self)
            # Environment variables setup todo

            # Start the process
            self.process = subprocess.run(
                self.cmd.split(),
                shell=True,
                text=True,
                stdout=open(self.stdout, "w"),
                stderr=open(self.stderr, "w"),
                cwd=self.workingdir,
            )
            # Wait for the process to start successfully
            time.sleep(self.starttime)
        except Exception as e:
            # Handle errors in process starting
            logger.error(f"Error starting process: {e}")
        logger.info(f"Task {self.name} started successfully")

    def stop(self):
        logger.info(f"Stopping task {self.name}")
        if not self.process:
            logger.info(f"Task {self.name} is already stopped")
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
