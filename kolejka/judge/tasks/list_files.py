import glob
import itertools
from functools import partial
from typing import Tuple, Optional

from kolejka.judge.tasks.base import Task


class ListFilesTask(Task):
    def __init__(self, *args, variable_name):
        self.files = list(args)
        self.variable_name = variable_name

    def execute(self, name, environment) -> Tuple[Optional[str], Optional[object]]:
        files = list(itertools.chain.from_iterable(map(partial(glob.glob, recursive=True), self.files)))
        environment.set_variable(self.variable_name, files)

        return None, None