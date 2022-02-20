from argparse import (
    ArgumentParser as _ArgumentParser,
    Action as _Action,
    Namespace as _Namespace,
    FileType as _FileType,
)
from typing import Any, Callable, Iterable, Optional, Sequence, Type, TypeVar, Union


_T = TypeVar("_T")
NOTSET = object()


class ArgumentParser(_ArgumentParser):
    def add_argument(
        self,
        *name_or_flags: str,
        action: Union[str, Type[_Action]] = ...,
        nargs: Union[int, str] = ...,
        const: Any = ...,
        default: Any = NOTSET,
        type: Union[Callable[[str], _T], Callable[[str], _T], _FileType] = ...,
        choices: Iterable[_T] = ...,
        required: bool = ...,
        help: Optional[str] = ...,
        metavar: Optional[Union[str, tuple[str, ...]]] = ...,
        dest: Optional[str] = ...,
        version: str = ...,
        **kwargs: Any,
    ) -> _Action:
        return super().add_argument(
            *name_or_flags,
            action=action,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar,
            dest=dest,
            version=version,
            **kwargs,
        )


class Namespace(_Namespace):
    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in vars(self).items() if value is not None}


class CLIArgs:
    def __init__(self, args: Sequence[str] | None = None):
        self._args = args
        self._remaining_args = args

    def parse_args(self, parser: ArgumentParser) -> Namespace:
        """Applies an argparse parser to the remaining arguments."""
        namespace, self._remaining_args = parser.parse_known_args(self._remaining_args)
        return namespace

    def parse_all_args(self, parser: ArgumentParser) -> Namespace:
        """Applies an argparse parser to all arguments that were passed to the app."""
        namespace, _ = parser.parse_known_args(self._args)
        return namespace
