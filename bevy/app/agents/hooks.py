from __future__ import annotations
from asyncio import gather
from collections import defaultdict
from copy import deepcopy
from inspect import getmro
from typing import Awaitable, Callable, cast, Generator, Iterable, ParamSpec, TypeVar


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

    def dispatch_to_hook(
        self, hook_name: str, *args: P.args, **kwargs: P.kwargs
    ) -> Awaitable:
        return gather(
            *self.__run_callbacks(self.__get_callbacks(hook_name), *args, **kwargs)
        )

    def __get_callbacks(self, hook_name: str) -> Generator[None, Callable[P, R], None]:
        yield from (
            getattr(self, name) for name in type(self).__bevy_hooks__[hook_name]
        )

    def __run_callbacks(
        self, callbacks: Iterable[Callable[P, R]], *args: P.args, **kwargs: P.kwargs
    ) -> Generator[None, Awaitable, None]:
        yield from (
            ret
            for callback in callbacks
            if isawaitable(ret := self.__run_callback(callback, *args, **kwargs))
        )

    def __run_callback(self, callback, *args, **kwargs) -> Awaitable | None:
        return callback(*args, **kwargs)


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
