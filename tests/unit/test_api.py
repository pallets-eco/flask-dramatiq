import pytest

def test_global_app(mocker):
    from flask import Flask
    from flask_dramatiq import Dramatiq
    from dramatiq.brokers.stub import StubBroker

    app = Flask('test')
    dramatiq = Dramatiq(app, broker_cls=StubBroker)

    @dramatiq.actor
    def myactor():
        pass

    assert hasattr(dramatiq, 'broker')


importable_object = object()


def test_importer():
    from flask_dramatiq import import_object

    obj = import_object(__name__ + ':importable_object')
    assert obj is importable_object

    with pytest.raises(ImportError):
        import_object(__name__ + '.absent:none')

    with pytest.raises(ImportError):
        import_object(__name__ + ':absent')
