import os
from copy import deepcopy
from pathlib import Path
from typing import Optional, List

from exceptions import PrerequisiteException


class CommandBase:
    name = ''
    result = None

    def __init__(self, limits=None):
        self.limits = limits or {}

    def _get_file_name(self, suffix):
        return Path('logs/{}_{}.txt'.format(self.name, suffix))

    def get_env(self):
        return deepcopy(os.environ)

    def get_limits(self):
        return self.limits or {}

    def get_command(self) -> List[object]:
        raise NotImplementedError

    def get_stdin_file(self) -> Optional[str]:
        return None

    def get_stdout_file(self) -> Optional[str]:
        return self._get_file_name('stdout')

    def get_stderr_file(self) -> Optional[str]:
        return self._get_file_name('stderr')

    def postconditions(self):
        return []

    def verify_postconditions(self, result):
        for postcondition, status in self.postconditions():
            if not postcondition(result):
                return status

    def prerequisites(self):
        return []

    def verify_prerequisites(self):
        for prerequisite in self.prerequisites():
            if not prerequisite():
                raise PrerequisiteException("Prerequisite `{}` not satisfied".format(prerequisite))

    def set_name(self, name):
        self.name = name

    def get_configuration_status(self):
        """
        :return: 2-tuple - (is the command configured correctly to be run (e.g. file extension is known), exit status)
        """
        return True, None
