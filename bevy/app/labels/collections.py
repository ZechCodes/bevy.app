from bevy.app.labels.indexes import LabelIndex
from bevy.app.labels.labels import LabelValue, LabelProtocol
from typing import Generic, TypeVar


T = TypeVar("T", bound=LabelProtocol)
NOT_SET = object()


class LabelCollection(Generic[T]):
    __bevy_indexes__: list[LabelIndex] = []

    def __init__(self):
        self._items: set[T] = set()

    def add(self, item: T):
        self._items.add(item)
        self._add_to_indexes(item)

    def _add_to_indexes(self, item: T):
        for index in self.__bevy_indexes__:
            index.add(item)

    def remove(self, item: T):
        self._items.add(item)
        self._add_to_indexes(item)

    def _remove_from_indexes(self, item: T):
        for index in self.__bevy_indexes__:
            index.remove(item)

    def get(self, **labels: LabelValue) -> tuple[T, ...]:
        return tuple(
            [item for item in self._items if self._label_matches(item, labels)]
        )

    def _label_matches(self, item: T, labels: dict[str, LabelValue]) -> bool:
        return all(
            item.labels.get(key, NOT_SET) == value for key, value in labels.items()
        )
