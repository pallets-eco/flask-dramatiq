from importlib import import_module
from threading import local

import click
from dramatiq import (
    Middleware,
    actor as register_actor,
    set_broker,
)
from dramatiq.cli import (
    CPUS,
    main as dramatiq_worker,
    make_argument_parser as dramatiq_argument_parser,
)
from flask.cli import with_appcontext


def import_object(path):
    # Implement setuptools entrypoint-like loading of object.
    modname, objname = path.split(':')
    mod = import_module(modname)
    return getattr(mod, objname)


class AppContextMiddleware(Middleware):
    # Setup Flask app for actor. Borrowed from
    # https://github.com/Bogdanp/flask_dramatiq_example.

    state = local()

    def __init__(self, app):
        self.app = app

    def before_process_message(self, broker, message):
        context = self.app.app_context()
        context.push()

        self.state.context = context

    def after_process_message(
            self, broker, message, *, result=None, exception=None):
        try:
            context = self.state.context
            context.pop(exception)
            del self.state.context
        except AttributeError:
            pass

    after_skip_message = after_process_message


class Dramatiq:
    # The Flask extension.

    def __init__(self, app=None):
        self.actors = []
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        # Reuse same defaults as dramatiq. cf.
        # https://github.com/Bogdanp/dramatiq/blob/master/dramatiq/broker.py#L34-L44
        app.config.setdefault(
            'DRAMATIQ_BROKER', 'dramatiq.brokers.rabbitmq:RabbitmqBroker')
        app.config.setdefault('DRAMATIQ_BROKER_URL', None)
        cls = import_object(app.config['DRAMATIQ_BROKER'])
        broker = cls(url=app.config['DRAMATIQ_BROKER_URL'])
        broker.add_middleware(AppContextMiddleware(app))
        set_broker(broker)

        for actor in self.actors:
            actor.register()

    def actor(self, fn=None, **kw):
        # Substitude dramatiq.actor decorator to return a lazy wrapper. This
        # allow to register actors in extension before the broker is
        # effectively configured by init_app.

        def decorator(fn):
            lazy_actor = LazyActor(self, fn, kw)
            self.actors.append(lazy_actor)
            if self.app:
                lazy_actor.register()
            return lazy_actor

        if fn:
            return decorator(fn)
        return decorator


class LazyActor(object):
    # Intermediate object that register actor on broker an call.

    def __init__(self, extension, fn, kw):
        self.extension = extension
        self.fn = fn
        self.kw = kw
        self.actor = None

    def register(self):
        self.actor = register_actor(**self.kw)(self.fn)

    # Next is regular actor API.

    def send(self, *a, **kw):
        return self.actor.send(*a, **kw)

    def send_with_options(self, *a, **kw):
        return self.actor.send_with_options(*a, **kw)


@click.command()
@click.option('-p', '--processes', default=CPUS,
              metavar='PROCESSES', show_default=True,
              help="the number of worker processes to run")
@click.option('-t', '--threads', default=8,
              metavar='THREADS', show_default=True,
              help="the number of worker treads per processes")
@click.option('-q', '--queues', type=str, default=None,
              metavar='QUEUES', show_default=True,
              help="listen to a subset of queues, comma separated")
@with_appcontext
def worker(processes, threads, queues):
    """
    Run dramatiq workers.

    Setup Dramatiq with broker and task modules from Flask app.

    \b
    examples:
      # Run dramatiq with 1 thread per process.
      $ flask worker --threads 1

    \b
      # Listen only to the "foo" and "bar" queues.
      $ flask worker -Q foo,bar

    """
    # Plugin for flask.commands entrypoint.
    #
    # Wraps dramatiq worker CLI in a Flask command. This is private API of
    # dramatiq.

    parser = dramatiq_argument_parser()
    command = [
        "--processes", str(processes),
        "--threads", str(threads),
        __name__,
    ]
    if queues:
        command += ["--queues"] + queues.split(",")
    args = parser.parse_args(command)
    dramatiq_worker(args)
