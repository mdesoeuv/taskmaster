from dataclasses import dataclass, field
import logging
import os
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
    process: subprocess.run = field(init=False, default=None)

    def start(self):
        if self.process and self.process.poll() is None:
            # Process is already running
            return
        try:
            print(self)
            # Environment variables setup
            env = os.environ.copy()
            if self.env:
                env.update(self.env)

            # Start the process
            self.process = subprocess.run(
                self.cmd.split(), shell=True,  text=True,
                stdout=open(self.stdout, "w"), stderr=open(self.stderr, "w"),
                env=env, cwd=self.workingdir,
            )
            # Wait for the process to start successfully
            time.sleep(self.starttime)

            # Check if the process started successfully
            if self.process.poll() is not None:
                # Process failed to start
                raise Exception("Process failed to start")
        except Exception as e:
            # Handle errors in process starting
            logger.error(f"Error starting process: {e}")

    def stop(self):
        if not self.process or self.process.poll() is not None:
            # Process is not running
            return
        try:
            # Send the stop signal
            self.process.send_signal(
                getattr(signal, f"SIG{self.stopsignal.name}")
            )
            # Wait for process to stop
            start_time = time.time()
            while time.time() - start_time < self.stoptime:
                if self.process.poll() is not None:
                    return  # Process stopped gracefully
                time.sleep(0.5)
            # Force kill if not stopped
            self.process.kill()
        except Exception as e:
            # Handle errors in stopping process
            logger.error(f"Error stopping process: {e}")

    def restart(self):
        self.stop()
        self.start()
