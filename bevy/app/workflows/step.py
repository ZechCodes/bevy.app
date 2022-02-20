from abc import ABC, abstractmethod
from asyncio import BaseEventLoop, Future
from inspect import isawaitable
from typing import Awaitable, Callable


class Step:
    def __init__(
        self, callback: Callable[[], Awaitable | None], *, schedule: str = "default"
    ):
        self.callback = callback
        self.scheduling_strategy = {
            "default": SequentialSchedulingStrategy,
            "concurrent": ConcurrentSchedulingStrategy,
            "deferred": DeferredSchedulingStrategy,
        }[schedule](self.run)

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


class AbstractSchedulingStrategy(ABC):
    def __init__(self, callback: Callable[[], Awaitable]):
        self.callback = callback

    @abstractmethod
    def schedule(
        self, *, previous: Future, workflow_complete: Future, loop: BaseEventLoop
    ) -> Awaitable | None:
        ...


class SequentialSchedulingStrategy(AbstractSchedulingStrategy):
    """Schedules the callback to be run after all the previous future resolves. The callback will block other callbacks
    in the workflow from running."""

    def schedule(self, *, previous: Future, loop: BaseEventLoop, **_) -> Awaitable:
        return loop.create_task(self._wait_for_previous(previous))

    async def _wait_for_previous(self, previous: Future):
        await previous
        await self.callback()


class ConcurrentSchedulingStrategy(SequentialSchedulingStrategy):
    """Schedules the callback to be run concurrently once the previous futures resolve. The callback will not block
    other callbacks from being called in the workflow."""

    def schedule(self, *, previous: Future, loop: BaseEventLoop, **_) -> None:
        loop.create_task(self._wait_for_previous(previous))
        return None


class DeferredSchedulingStrategy(AbstractSchedulingStrategy):
    """Schedules the callback to be called once the workflow completes."""

    def schedule(self, *, workflow_complete: Future, loop: BaseEventLoop, **_) -> None:
        loop.create_task(self._deferred_run(workflow_complete))
        return None

    async def _deferred_run(self, workflow_complete: Future):
        await workflow_complete
        await self.callback()
