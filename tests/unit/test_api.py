import pytest


def test_global_app():
    from dramatiq.brokers.stub import StubBroker
    from flask import Flask
    from flask_dramatiq import Dramatiq

    app = Flask("test")
    dramatiq = Dramatiq(app, broker_cls=StubBroker)

    @dramatiq.actor
    def myactor():
        pass

    assert hasattr(dramatiq, "broker")


importable_object = object()


def test_importer():
    from flask_dramatiq import import_object

    obj = import_object(__name__ + ":importable_object")
    assert obj is importable_object

    with pytest.raises(ImportError):
        import_object(__name__ + ".absent:none")

    with pytest.raises(ImportError):
        import_object(__name__ + ":absent")


def test_named_ext():
    from flask_dramatiq import Dramatiq

    my = Dramatiq(name="my")

    assert "my" in repr(my)
