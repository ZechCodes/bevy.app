from bevy.app.labels.labels import LabelProtocol, LabelValue
from collections import defaultdict
from weakref import WeakSet
from typing import Any, Generic, TypeVar, Iterable, overload


T = TypeVar("T", bound=LabelProtocol)
Index = dict[tuple[str, ...], WeakSet[T]]

NOT_SET = object()


class LabelIndex(Generic[T]):
    def __init__(self, *keys: str):
        self._keys = keys
        self._index: Index = defaultdict(WeakSet)

    @overload
    def __getitem__(self, values: LabelValue) -> tuple[T, ...]:
        ...

    @overload
    def __getitem__(self, values: tuple[LabelValue, ...]) -> tuple[T, ...]:
        ...

    def __getitem__(self, values: tuple[LabelValue, ...] | LabelValue) -> tuple[T, ...]:
        values = tuple(values) if isinstance(values, Iterable) else (values,)
        return tuple(
            [
                item
                for item in self._index[values]
                if self._matches_label(item, **self._get_named_values(values))
            ]
        )

    def __set_name__(self, owner, name):
        owner.__bevy_indexes__.append(self)

    def get(
        self, *values: LabelValue, default: Any | None = None
    ) -> tuple[T, ...] | Any | None:
        if values not in self._index or not self._index[values]:
            return default

        return self[values]

    def add(self, item: T):
        self._index[self._get_key(item)].add(item)

    def remove(self, item: T, *values: LabelValue):
        key = values or self._get_key(item)
        self._index[key].remove(item)

    def _get_key(self, item: T) -> tuple[LabelValue, ...]:
        return tuple(item.labels[key] for key in self._keys)

    def _get_named_values(
        self, values: tuple[LabelValue, ...]
    ) -> dict[str, LabelValue]:
        return dict(zip(self._keys, values))

    def _matches_label(self, item: LabelProtocol, **values: LabelValue) -> bool:
        return all(item.labels.get(key, NOT_SET) == values[key] for key in self._keys)
