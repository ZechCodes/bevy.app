from bevy import AutoInject, detect_dependencies
from bevy.builder import Builder
from bevy.workflows.step import Step, AsyncStep, DeferredStep, SequentialStep
from bevy.workflows.workflow import Workflow
from pathlib import Path
from typing import Any, Type
import json


@detect_dependencies
class WorkflowBuilder(AutoInject):
    make_workflow: Builder[Workflow]

    def __init__(self):
        self._step_types: dict[str, Type[Step]] = {
            "async": AsyncStep,
            "deferred": DeferredStep,
            "sequential": SequentialStep,
        }

    def create_workflows_from_file(self, path: Path) -> list[Workflow]:
        data = self._load_workflow_file(path)
        return self._create_workflows(data.get("workflows", []))

    def _create_workflows(self, data: list[dict[str, Any]]) -> list[Workflow]:
        return [self._create_workflow(workflow_data) for workflow_data in data]

    def _create_workflow(self, data: dict[str, Any]) -> Workflow:
        return self.make_workflow(
            data,
            [self._create_step(step) for step in data["steps"]],
        )

    def _create_step(self, data: dict[str, Any]) -> Step:
        agents = self._find_agents(data["agent"])
        callback = self._create_agents_caller(agents, data["action"])
        step_type = self._step_types[data.get("type", "sequential")]
        return self.__bevy_context__.bind(step_type)(callback, **data)

    def _load_workflow_file(self, path: Path) -> dict[str, Any]:
        with path.open("r") as workflow_file:
            return json.load(workflow_file)
