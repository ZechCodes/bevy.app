from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop, Future
from inspect import isawaitable
from typing import Awaitable, Callable


class Step(ABC):
    def __init__(self, callback: Callable[[], Awaitable | None], **kwargs):
        self.callback = callback

    @abstractmethod
    def launch(
        self, *, prev_step: Future, workflow_complete: Future, loop: AbstractEventLoop
    ) -> Awaitable | None:
        ...

    async def run(self):
        ret = self.callback()
        if isawaitable(ret):
            await ret


class SequentialStep(Step):
    """Sequential steps run one after the other."""

    def launch(self, *, prev_step: Future, loop: AbstractEventLoop, **_) -> Awaitable:
        return loop.create_task(self._wait_for_previous(prev_step))

    async def _wait_for_previous(self, prev_step: Future):
        await prev_step
        await self.run()


class AsyncStep(SequentialStep):
    """Async steps run immediately after being started."""

    def launch(self, *, prev_step: Future, loop: AbstractEventLoop, **_) -> None:
        loop.create_task(self._wait_for_previous(prev_step))
        return None


class DeferredStep(Step):
    """Deferred steps run once the workflow completes."""

    def launch(
        self, *, workflow_complete: Future, loop: AbstractEventLoop, **_
    ) -> None:
        loop.create_task(self._deferred_run(workflow_complete))
        return None

    async def _deferred_run(self, workflow_complete: Future):
        await workflow_complete
        await self.run()
