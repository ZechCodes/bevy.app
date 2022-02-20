import asyncio


class AwaitAllNewTasks:
    def __init__(self, loop: asyncio.BaseEventLoop | None = None):
        self.loop = loop
        self.tasks = set()

    async def __aenter__(self):
        self.tasks = asyncio.all_tasks(self.loop)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await asyncio.gather(*(asyncio.all_tasks(self.loop) - self.tasks))
