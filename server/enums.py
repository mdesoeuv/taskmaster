import logging
from enum import Enum
import signal

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)

SIGNAL_MAP = {
    "TERM": signal.SIGTERM,
    "HUP": signal.SIGHUP,
    "INT": signal.SIGINT,
    "QUIT": signal.SIGQUIT,
    "KILL": signal.SIGKILL,
    "USR1": signal.SIGUSR1,
    "USR2": signal.SIGUSR2,
}


class Signal:
    def __init__(self, sig: str = "TERM"):
        self.signal = SIGNAL_MAP[sig]


class Status(str, Enum):
    STARTING = "STARTING"
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    EXITED = "EXITED"
    FATAL = "FATAL"
    STOPPING = "STOPPING"
    ABORTED = "ABORTED"

    def __str__(self):
        return self.value


class AutoRestart(str, Enum):
    unexpected = "unexpected"
    true = "true"
    false = "false"
