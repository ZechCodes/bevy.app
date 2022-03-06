from asyncio import BaseEventLoop, Future
from inspect import isawaitable
from typing import Awaitable, Callable

from bevy.app.workflows.scheduling import SchedulingStrategyRegistry
from bevy.injection import AutoInject, detect_dependencies


@detect_dependencies
class Step(AutoInject):
    _scheduling_strategies: SchedulingStrategyRegistry

    def __init__(
        self, callback: Callable[[], Awaitable | None], *, schedule: str = "sequential"
    ):
        self.callback = callback
        self.scheduling_strategy = self._scheduling_strategies.create(
            schedule, self.run
        )

    def launch(
        self, *, prev_step: Future, workflow_complete: Future, loop: BaseEventLoop
    ) -> Awaitable | None:
        return self.scheduling_strategy.schedule(
            previous=prev_step, workflow_complete=workflow_complete, loop=loop
        )

    async def run(self):
        ret = self.callback()
        if isawaitable(ret):
            await ret

    def __repr__(self):
        return f"{type(self).__name__}({self.action!r}, *, schedule={self.scheduling_strategy!r}, name={self.name!r})"
