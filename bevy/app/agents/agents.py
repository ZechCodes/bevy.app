from __future__ import annotations

from typing import Any, cast, Type, TypeVar

from bevy.injection import AutoInject, detect_dependencies

from bevy.app.agents.hooks import Hookable
from bevy.app.labels.collections import LabelCollection, LabelIndex
from bevy.app.labels.labels import Labels


T = TypeVar("T", bound="Agent")


class Agent(Hookable):
    labels = Labels(type="agent")


@detect_dependencies
class AgentCollection(LabelCollection[Agent], AutoInject):
    type = LabelIndex("type")

    def create(self, agent_type: Type[T], *args, **kwargs) -> T:
        return self.factory(agent_type)(*args, **kwargs)

    async def dispatch(
        self,
        hook_name: str,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
        labels: dict[str, Any] | None = None,
    ):
        for agent in self.get(**labels or {}):
            await agent.dispatch_to_hook(hook_name, *args or [], **kwargs or {})

    def factory(self, agent_type: Type[T]) -> Type[T]:
        constructor = self.__bevy_context__.bind(agent_type)

        def create(*args, **kwargs) -> T:
            self.add(instance := constructor(*args, **kwargs))
            return instance

        return cast(Type[T], create)
