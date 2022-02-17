from __future__ import annotations
from collections import UserDict
from typing import Protocol, Type, TypeVar


class LabelProtocol(Protocol):
    labels: Labels


LabelValue = str | int | float | bool
T = TypeVar("T", bound=LabelProtocol)


class Labels(UserDict):
    def __get__(self, instance: T | None, owner: Type[T]) -> Labels:
        if instance:
            instance.labels = self.copy()

        return instance.labels
