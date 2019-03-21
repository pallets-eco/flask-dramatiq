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
