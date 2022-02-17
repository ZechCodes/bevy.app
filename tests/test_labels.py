from bevy.app.labels import Labels, LabelCollection, LabelIndex
from itertools import count


def test_label_lookup():
    class TestLabelCollection(LabelCollection):
        ...

    class Obj:
        next_id = count()
        labels = Labels(type="Test")

        def __init__(self):
            self.labels["id"] = next(Obj.next_id)

    collection = TestLabelCollection()
    collection.add(Obj())
    collection.add(Obj())
    collection.add(Obj())
    collection.add(Obj())

    assert len(collection.get(type="Test")) == 4
    assert len(collection.get(id=2)) == 1
    assert len(collection.get(invalid=True)) == 0


def test_label_indexes():
    class TestLabelCollection(LabelCollection):
        id = LabelIndex("id")
        type_and_id = LabelIndex("type", "id")

    class Obj:
        next_id = count()
        labels = Labels(type="Test")

        def __init__(self, use_id=None):
            self.labels["id"] = next(Obj.next_id) if use_id is None else use_id

    collection = TestLabelCollection()
    collection.add(Obj())
    collection.add(Obj())
    collection.add(Obj())
    collection.add(Obj())
    collection.add(Obj(2))

    assert len(collection.id[3]) == 1
    assert len(collection.type_and_id["Test", 2]) == 2
