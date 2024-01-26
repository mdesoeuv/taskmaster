from dataclasses import dataclass
from typing import List
from enum import Enum


class Signal(Enum):
    TERM = "TERM"
    HUP = "HUP"
    INT = "INT"
    QUIT = "QUIT"
    KILL = "KILL"


@dataclass
class Task:
    cmd: str
    numprocs: int = 1
    umask: str = "022"
    workingdir: str = "/tmp"
    autostart: bool = True
    autorestart: bool = True
    exitcodes: List[int] = [0, 1]
    startretries: int = 3
    starttime: int = 0
    stopsignal: Signal = Signal.TERM
    stoptime: int = 10
    stdout: str = "/dev/null"
    stderr: str = "/dev/null"
    env: dict = None

    def start(self):
        print(f"Démarrage de la tâche : {self.cmd}")

    def stop(self):
        print(f"Arrêt de la tâche avec le signal : {self.stopsignal}")
