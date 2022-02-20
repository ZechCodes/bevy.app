from __future__ import annotations
from bevy.injection import AutoInject, detect_dependencies
from bevy.app.agents.hooks import Hookable
from bevy.app.labels.collections import LabelCollection, LabelIndex
from typing import cast, Type, TypeVar


T = TypeVar("T", bound="Agent")


@detect_dependencies
class AgentCollection(LabelCollection, AutoInject):
    type = LabelIndex("type")

    def create(self, agent_type: Type[T], *args, **kwargs) -> T:
        return self.factory(agent_type)(*args, **kwargs)

    def factory(self, agent_type: Type[T]) -> Type[T]:
        constructor = self.__bevy_context__.bind(agent_type)

        def create(*args, **kwargs) -> T:
            self.add(instance := constructor(*args, **kwargs))
            return instance

        return cast(Type[T], create)


class Agent(Hookable):
    ...
