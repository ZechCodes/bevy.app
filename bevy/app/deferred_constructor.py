from typing import Generic, Type, TypeVar

from bevy.injection import Context


T = TypeVar("T")


class DeferredConstructorMetaclass(type):
    def __call__(cls, *args, **kwargs):
        return DeferredConstructor(cls, *args, **kwargs)


class DeferConstructor(Generic[T], metaclass=DeferredConstructorMetaclass):
    ...


class DeferredConstructor(Generic[T]):
    def __init__(self, cls: Type[T], *args, **kwargs):
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def __bevy_builder__(self, context: Context) -> T:
        return lambda: context.bind(self.cls)(*self.args, **self.kwargs)

    def __repr__(self):
        args = [self.cls.__name__]
        args.extend(map(repr, self.args))
        args.extend(f"{name}={value!r}" for name, value in self.kwargs.items())

        return f"{type(self).__name__}({', '.join(args)})"
