import pytest
from bevy.injection import Context

from bevy.app.agents import Agent, AgentCollection, hook
from bevy.app.ext import RunWorkflowAction, TriggerAgentHookAction
from bevy.app.labels import Labels
from bevy.app.utils import apply, AwaitAllNewTasks
from bevy.app.workflows import Step, Workflow, WorkflowCollection


@pytest.mark.asyncio
async def test_deferred_steps():
    result = []

    class TestAgent(Agent):
        labels = Labels(type="test")

        @hook("test-hook")
        def test_hook(self):
            result.append("RAN")

    context = Context() << (WorkflowCollection @ Context) << (AgentCollection @ Context)
    workflows = WorkflowCollection << context
    workflows.add(
        Workflow(
            labels=Labels(type="launch"),
            steps=[Step(RunWorkflowAction(Labels(type="run")))],
        )
    )
    workflows.add(
        Workflow(
            labels=Labels(type="run"),
            steps=[Step(TriggerAgentHookAction("test-hook", Labels(type="test")))],
        )
    )
    (AgentCollection << context).add(TestAgent @ context)

    async with AwaitAllNewTasks():
        await apply(Workflow.run, workflows.get(type="launch"))

    assert result == ["RAN"]
