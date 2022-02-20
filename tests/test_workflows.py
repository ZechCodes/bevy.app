from bevy.app.workflows.step import Step
from bevy.app.workflows.workflow import Workflow
from bevy.app.utils import AwaitAllNewTasks
import asyncio
import pytest


@pytest.mark.asyncio
async def test_sequential_steps():
    result = []

    def action_factory(n, delay=0.1):
        async def action():
            await asyncio.sleep(delay)
            result.append(n)

        return action

    workflow = Workflow()
    for n in range(3):
        workflow.step(Step(action_factory(n)))

    async with AwaitAllNewTasks():
        await workflow.run()

    assert result == [0, 1, 2]


@pytest.mark.asyncio
async def test_concurrent_steps():
    result = []

    def action_factory(n, delay=0.1):
        async def action():
            await asyncio.sleep(delay)
            result.append(n)

        return action

    workflow = Workflow()
    workflow.step(Step(action_factory(-1, delay=0.5), schedule="concurrent"))
    for n in range(3):
        workflow.step(Step(action_factory(n)))

    workflow.step(Step(action_factory(-2, delay=0.05), schedule="concurrent"))

    async with AwaitAllNewTasks():
        await workflow.run()

    assert result == [0, 1, 2, -2, -1]


@pytest.mark.asyncio
async def test_deferred_steps():
    result = []

    def action_factory(n, delay=0.1):
        async def action():
            await asyncio.sleep(delay)
            result.append(n)

        return action

    workflow = Workflow()
    for n in range(3):
        workflow.step(Step(action_factory(n)))

    workflow.step(Step(action_factory(-1, delay=0.05), schedule="deferred"))

    async with AwaitAllNewTasks():
        await workflow.run()

    assert result == [0, 1, 2, -1]
