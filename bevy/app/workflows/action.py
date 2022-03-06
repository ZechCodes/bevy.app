from bevy.injection import AutoInject

from bevy.app.deferred_constructor import DeferConstructor


class Action(DeferConstructor, AutoInject):
    def run(self):
        raise NotImplemented()
