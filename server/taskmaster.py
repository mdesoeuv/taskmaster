from dataclasses import dataclass, field
from yamldataclassconfig.config import YamlDataClassConfig
from definitions import ProgramDefinition
from program import Program
from typing import Dict
import pathlib
import asyncio


@dataclass
class TaskMaster(YamlDataClassConfig):
    config_file: pathlib.Path
    programs_definition: Dict[str, ProgramDefinition] = field(
        default_factory=dict
    )
    programs: Dict[str, Program] = field(default_factory=dict)
    active_connections: Dict[str, asyncio.StreamWriter] = field(
        default_factory=dict
    )
