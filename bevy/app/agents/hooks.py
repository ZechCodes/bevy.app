from __future__ import annotations
from collections import defaultdict
from typing import Callable, cast, ParamSpec, TypeVar
from copy import deepcopy
from inspect import getmro


P = ParamSpec("P")
R = TypeVar("R")


class HookClassRepository:
    def __init__(self):
        self.repo = {}

    def __get__(self, _, owner: Hookable) -> dict[str, set[str]]:
        if id(owner) not in self.repo:
            self.repo[id(owner)] = self.build_hook_dict(owner)

        return self.repo[id(owner)]

    def build_hook_dict(self, owner):
        for super_ in getmro(owner):
            if super_ is not owner and hasattr(super_, "__bevy_hooks__"):
                return deepcopy(super_.__bevy_hooks__)

        return defaultdict(set)


class Hookable:
    __bevy_hooks__: dict[str, set[str]] = HookClassRepository()


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
