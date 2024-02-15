from dataclasses import dataclass
from yamldataclassconfig.config import YamlDataClassConfig
from program_definition import ProgramDefinition
from program import Program
from typing import Dict
import pathlib


@dataclass
class TaskMaster(YamlDataClassConfig):
    config_file: pathlib.Path
    programs_definition: Dict[str, ProgramDefinition] = {}
    programs: Dict[str, Program] = {}
