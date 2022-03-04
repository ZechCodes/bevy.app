import asyncio
from itertools import starmap
from typing import Any, TypeVar

from bevy.app.labels import Labels
from bevy.app.options import Options
from bevy.app.workflows.step import Step
from bevy.injection import AutoInject, detect_dependencies

Self = TypeVar("Self", bound="Workflow")


class NullFuture(asyncio.Future):
    def done(self) -> bool:
        return True

    def __await__(self):
        yield from []


@detect_dependencies
class Workflow(AutoInject):
    options: Options

    def __init__(self):
        self._labels = Labels()
        self._steps = []
        self._namespace = {}

    @property
    def labels(self) -> Labels:
        return self._labels

    @property
    def steps(self) -> list[Step]:
        return self._steps

    def label(self: Self, **labels) -> Self:
        self._labels |= labels
        return self

    def step(self: Self, step: Step) -> Self:
        self._steps.append(step)
        return self

    def value(self: Self, **values) -> Self:
        self._namespace |= starmap(self._process_value, values.items())
        return self

    async def run(self, loop: asyncio.AbstractEventLoop | None = None):
        loop = loop or asyncio.get_running_loop()
        prev_step = NullFuture(loop=loop)
        done = asyncio.Future()
        tasks = []
        for step in self.steps:
            task = step.launch(prev_step=prev_step, workflow_complete=done, loop=loop)
            if task:
                prev_step = task
                tasks.append(prev_step)

        await asyncio.gather(*tasks)
        done.set_result(True)

    def _process_value(self, key: str, value: Any) -> tuple[str, Any]:
        match key[0], key[1:]:
            case "$", key:
                return key, value.format(**self._namespace)
            case "@", key:
                return key, self.options[value]
            case _:
                return key, value
