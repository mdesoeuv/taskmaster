class TaskException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ProgramDefinitionError(TaskException):
    def __init__(self, message):
        super().__init__(message)


class ConfigError(TaskException):
    def __init__(self, message):
        super().__init__(message)


class ProcessException(Exception):
    def __init__(self, message):
        super().__init__(message)
