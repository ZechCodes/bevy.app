from asyncio import BaseEventLoop, Future
from inspect import isawaitable
from typing import Awaitable

from bevy.injection import AutoInject, detect_dependencies

from bevy.app.deferred_constructor import DeferConstructor
from bevy.app.workflows.action import Action
from bevy.app.workflows.scheduling import SchedulingStrategyRegistry


@detect_dependencies
class Step(DeferConstructor, AutoInject):
    _scheduling_strategies: SchedulingStrategyRegistry

    def __init__(
        self, action: Action, *, schedule: str = "sequential", name: str | None = None
    ):
        self.name = name
        self.action = action @ self.__bevy_context__
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
        ret = self.action.run()
        if isawaitable(ret):
            await ret

    def __repr__(self):
        return f"{type(self).__name__}({self.action!r}, *, schedule={self.scheduling_strategy!r}, name={self.name!r})"
