from bevy.app.agents.hooks import Hookable
from bevy.app.labels.collections import LabelCollection, LabelIndex


class AgentCollection(LabelCollection):
    type = LabelIndex("type")


class Agent(Hookable):
    ...
