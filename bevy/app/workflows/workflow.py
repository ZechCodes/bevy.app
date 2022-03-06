import asyncio
from typing import Any

from bevy.injection import AutoInject, detect_dependencies

from bevy.app.deferred_constructor import DeferConstructor, DeferredConstructor
from bevy.app.labels import Labels
from bevy.app.options import Options
from bevy.app.workflows.step import Step


class NullFuture(asyncio.Future):
    def done(self) -> bool:
        return True

    def __await__(self):
        yield from []


@detect_dependencies
class Workflow(DeferConstructor, AutoInject):
    app_options: Options

    def __init__(
        self,
        labels: Labels | None = None,
        steps: list[Step] | None = None,
        options: dict[str, Any] | None = None,
    ):
        self._labels = labels or Labels()
        self._steps = self._initialize_steps(steps or [])
        self._options = options or {}

    @property
    def labels(self) -> Labels:
        return self._labels

    @property
    def steps(self) -> list[Step]:
        return self._steps

    @property
    def options(self) -> dict[str, Any]:
        return self._options

    def value(self, **values):
        self._options |= values

    async def run(self, loop: asyncio.BaseEventLoop | None = None):
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

    def _initialize_steps(
        self, steps: list[DeferredConstructor[Step] | Step]
    ) -> list[Step]:
        return [
            step @ self.__bevy_context__
            if isinstance(step, DeferredConstructor)
            else step
            for step in steps
        ]

    def _process_value(self, key: str, value: Any) -> tuple[str, Any]:
        match key[0], key[1:]:
            case "$", key:
                return key, value.format(**self._options)
            case "@", key:
                return key, self.options[value]
            case _:
                return key, value

    def __repr__(self):
        return f"{type(self).__name__}({self.labels}, {self.steps}, {self.options})"
