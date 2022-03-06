from __future__ import annotations

import asyncio
from inspect import isawaitable
from typing import Awaitable, Callable, Iterable, TypeVar


T = TypeVar("T")
def apply(
    func: Callable[[T], Awaitable[None, None, None] | None], iterable: Iterable[T]
) -> asyncio.Future:
    """Simple function for applying a callable to each item in an iterable."""
    tasks = []
    for item in iterable:
        ret = func(item)
        if isawaitable(ret):
            tasks.append(ret)

    return asyncio.gather(*tasks)


class AwaitAllNewTasks:
    def __init__(self, loop: asyncio.BaseEventLoop | None = None):
        self.loop = loop
        self.tasks = set()

    async def __aenter__(self):
        self.tasks = asyncio.all_tasks(self.loop)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await asyncio.gather(*(asyncio.all_tasks(self.loop) - self.tasks))
