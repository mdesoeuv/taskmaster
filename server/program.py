import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List
from exceptions import ProcessException
from process import Process
from definitions import ProgramDefinition
from enums import Status

logger = logging.getLogger(__name__)


def compare_programs(
    old_program: ProgramDefinition, new_program: ProgramDefinition
) -> List[str]:

    differences = []

    for attr in new_program.__dict__.keys():
        if getattr(old_program, attr) != getattr(new_program, attr):
            differences.append(attr)
    return differences


def critical_attribute(attributes: List[str]) -> bool:
    critical = [
        "name",
        "cmd",
        "workingdir",
        "umask",
        "stdout",
        "stderr",
    ]
    intersection = list(set(attributes) & set(critical))
    if intersection:
        return True
    return False


@dataclass
class Program(ProgramDefinition):
    processes: Dict[int, Process] = field(default_factory=dict)
    state: Status = Status.STOPPED

    def __init__(self, program_definition: ProgramDefinition):
        # Init the ProgramDefinition attributes coming from herited class
        super().__init__(**program_definition.__dict__)
        # Init the Program attributes
        self.processes = {}

    def start(self):
        logger.info(f"Starting task {self.name}")
        self.state = Status.RUNNING
        errors = 0
        processes_already_started = 0
        try:
            for process_id in range(self.numprocs):
                try:
                    if self.processes.get(process_id) is not None and (
                        self.processes[process_id].status == Status.RUNNING
                        or self.processes[process_id].status == Status.STARTING
                    ):
                        logger.info(
                            f"Process {self.name}-{process_id} is already running"
                        )
                        processes_already_started += 1
                        continue
                    self.processes[process_id] = Process(
                        name=f"{self.name}-{process_id}",
                        cmd=self.cmd,
                        cwd=self.cwd,
                        env=self.env,
                        umask=self.umask,
                        stdout=self.stdout,
                        stderr=self.stderr,
                        exitcodes=self.exitcodes,
                        stopsignal=self.stopsignal,
                        starttime=self.starttime,
                        stoptime=self.stoptime,
                        autorestart=self.autorestart,
                        startretries=self.startretries,
                        mail_alerting=self.mail_alerting,
                    )
                    logger.debug(f"Starting process {self.name}-{process_id}")
                    asyncio.create_task(self.processes[process_id].start())
                    logger.debug(f"Process {self.name}-{process_id} started")
                except Exception as e:
                    raise ProcessException(
                        f"Error starting process {self.name}-{process_id}: {e}"
                    )
                logger.debug(
                    f"Task {self.name}: {process_id + 1}/{self.numprocs} started"
                )
        except Exception as e:
            logger.debug(f"Error starting Program: {e}")
            errors += 1
            return f"Error starting Program {self.name}: {self.numprocs - errors}/{self.numprocs} started successfully"
        if processes_already_started == self.numprocs:
            logger.info(f"Task {self.name} is already running")
            return f"Task {self.name} is already running"
        log_string = f"Task {self.name}: {self.numprocs - errors}/{self.numprocs} started successfully, {processes_already_started} already running, {errors} failed"
        logger.info(log_string)
        return log_string

    async def stop(self):
        self.state = Status.STOPPED
        logger.info(f"Stopping task {self.name}")
        try:
            # Wait for process to stop
            for process_id in range(self.numprocs):
                if not self.processes or not self.processes[process_id]:
                    logger.debug(
                        f"Process {self.name}-{process_id} is already stopped"
                    )
                    continue
                logger.debug(f"Stopping process {self.name}-{process_id}")
                await self.processes[process_id].stop()

        except Exception as e:
            logger.debug(f"Error stopping process: {e}")
            return f"Error stopping task {self.name}: {e}"
        logger.info(f"Task {self.name} stopped successfully")
        return f"Task {self.name} stopped successfully"

    def restart(self):

        self.kill()
        for process in self.processes.values():
            process.reset()
        self.start()
        return "Program restarted"

    def kill(self):
        self.state = Status.STOPPED
        for process in self.processes.values():
            process.kill()
        return "Program killed"

    def update(self, new_program: ProgramDefinition):
        # check if critical attributes have changed
        # kill -> all except :
        # numprocs
        # autostart
        # autorestart
        # exitcodes
        # startretries
        # starttime
        # stopsignal
        # stoptime
        # if yes, kill all processes and relaunch them
        # if no, update the program attributes
        # finally remove extra processes if numprocs has decreased or add new processes if numprocs has increased
        differences = compare_programs(self, new_program)
        print("Differences: ", differences)
        if not differences:
            logger.debug(f"No changes for process group {self.name}")
            return "Program unchanged"

        old_numprocs = self.numprocs
        old_state = self.state

        if critical_attribute(differences):
            logger.info(
                f"Critical attributes have changed for process group {self.name}. Reloading process group..."
            )
            self.kill()

        logger.debug(f"Updating process group {self.name}...")
        self.__dict__.update(new_program.__dict__)

        # Add new processes
        if self.numprocs > old_numprocs:
            logger.debug(
                f"Adding {self.numprocs - old_numprocs} new processes to process group {self.name}"
            )
            for process_id in range(old_numprocs, self.numprocs):
                self.processes[process_id] = Process(
                    name=f"{self.name}-{process_id}",
                    cmd=self.cmd,
                    cwd=self.cwd,
                    env=self.env,
                    umask=self.umask,
                    stdout=self.stdout,
                    stderr=self.stderr,
                    exitcodes=self.exitcodes,
                    stopsignal=self.stopsignal,
                    starttime=self.starttime,
                    stoptime=self.stoptime,
                    autorestart=self.autorestart,
                    startretries=self.startretries,
                )
        # Remove extra processes
        elif self.numprocs < old_numprocs:
            logger.debug(
                f"Removing {old_numprocs - self.numprocs} processes from process group {self.name}"
            )
            for process_id in range(self.numprocs, old_numprocs):
                self.processes[process_id].kill()
                del self.processes[process_id]
        logger.debug(f"Process group {self.name}: updating processes...")
        for process in self.processes.values():
            process.update(new_program)

        if self.autostart or old_state == Status.RUNNING:
            self.start()
        return "Program updated"

    def get_status(self) -> str:
        return_string = ""
        for process_id in range(self.numprocs):
            if self.processes.get(process_id):
                status = self.processes[process_id].status
                returncode = self.processes[process_id].returncode
                uptime = self.processes[process_id].get_uptime()
                if self.processes[process_id].process:
                    pid = self.processes[process_id].process.pid
                    return_string += f"{self.name}-{process_id}: {status} ({returncode}), pid {pid}, uptime {uptime}\n"
                else:
                    return_string += f"{self.name}-{process_id}: {status} ({returncode}), uptime {uptime}\n"
            else:
                return_string += f"{self.name}-{process_id}: STOPPED\n"
        return return_string
