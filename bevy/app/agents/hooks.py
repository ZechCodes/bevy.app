from __future__ import annotations
from collections import defaultdict
from typing import Callable, cast, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")


class Hookable:
    __bevy_hooks__ = defaultdict(set)


class Hook:
    def __init__(self, hook_name: str):
        self._hook_name = hook_name
        self._func = None

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        self._func = func
        return self

    def __set_name__(self, owner: Hookable, name: str):
        owner.__bevy_hooks__[self._hook_name].add(name)
        setattr(owner, name, self._func)


def hook(hook_name: str) -> Callable[P, R]:
    return cast(Callable[P, R], Hook(hook_name))
