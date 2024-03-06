from dataclasses import dataclass
from typing import List
from enums import AutoRestart


@dataclass
class ProgramDefinition:
    name: str
    cmd: str
    umask: int
    numprocs: int
    cwd: str
    autostart: bool
    autorestart: AutoRestart
    exitcodes: List[int]
    startretries: int
    starttime: int
    stopsignal: str
    stoptime: int
    stdout: str
    stderr: str
    env: dict
    mail_alerting: bool
