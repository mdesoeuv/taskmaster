from dataclasses import dataclass, field
from typing import List
from yamldataclassconfig.config import YamlDataClassConfig
from enums import AutoRestart, Signal


@dataclass
class ProgramDefinition(YamlDataClassConfig):
    name: str
    cmd: str
    numprocs: int = 1
    umask: str = "022"
    cwd: str = "/tmp"
    autostart: bool = True
    autorestart: AutoRestart = AutoRestart.unexpected
    exitcodes: List[int] = field(default_factory=lambda: [0, 1])
    startretries: int = 3
    starttime: int = 0
    stopsignal: str = Signal("TERM").signal
    stoptime: int = 10
    stdout: str = "/dev/null"
    stderr: str = "/dev/null"
    env: dict = None
