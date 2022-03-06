from typing import Any

from bevy.injection import detect_dependencies

from bevy.app.agents import AgentCollection
from bevy.app.labels import Labels
from bevy.app.workflows import WorkflowCollection
from bevy.app.workflows.action import Action


@detect_dependencies
class RunWorkflowAction(Action):
    workflows: WorkflowCollection

    def __init__(
        self,
        labels: Labels,
        options: dict[str, Any] | None = None,
        all_options: bool = False,
    ):
        self.labels = labels
        self.options = options or {}
        self.all_options = all_options

    async def run(self):
        for workflow in self.workflows.get(**self.labels):
            await workflow.run()

    def __repr__(self):
        return f"{type(self).__name__}({self.labels!r}, {self.options!r}, {self.all_options!r})"


@detect_dependencies
class TriggerAgentHookAction(Action):
    agents: AgentCollection

    def __init__(
        self,
        hook: str,
        labels: Labels | None = None,
        options: dict[str, Any] | None = None,
    ):
        self.hook = hook
        self.labels = labels or Labels()
        self.options = options or {}

    async def run(self):
        await self.agents.dispatch(self.hook, kwargs=self.options, labels=self.labels)

    def __repr__(self):
        return (
            f"{type(self).__name__}({self.hook!r}, {self.labels!r}, {self.options!r})"
        )
