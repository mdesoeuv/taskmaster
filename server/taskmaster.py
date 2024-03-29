from dataclasses import dataclass, field
from definitions import ProgramDefinition
from program import Program
from typing import Dict
import pathlib
import asyncio


@dataclass
class TaskMaster:
    config_file: pathlib.Path
    programs_definition: Dict[str, ProgramDefinition] = field(
        default_factory=dict
    )
    programs: Dict[str, Program] = field(default_factory=dict)
    server: asyncio.Server = None
    active_connections: Dict[str, asyncio.StreamWriter] = field(
        default_factory=dict
    )
