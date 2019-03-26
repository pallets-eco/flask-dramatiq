import os.path
import sys
from importlib import import_module
from threading import local
from warnings import warn

import click
from dramatiq import (
    Middleware,
    actor as register_actor,
    set_broker,
)
from dramatiq.cli import (
    CPUS,
    HAS_WATCHDOG,
    main as dramatiq_worker,
    make_argument_parser as dramatiq_argument_parser,
)
from dramatiq.middleware import default_middleware
from flask import current_app
from flask.cli import with_appcontext


def guess_code_directory(broker):
    actor = next(iter(broker.actors.values()))
    modname, *_ = actor.fn.__module__.partition('.')
    mod = sys.modules[modname]
    return os.path.dirname(mod.__file__)


def import_object(path):
    # Implement setuptools entrypoint-like loading of object.
    modname, objname = path.split(':')
    mod = import_module(modname)
    try:
        return getattr(mod, objname)
    except AttributeError:
        raise ImportError("%s does not exists." % path)


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

    # Reuse same defaults as dramatiq. cf.
    # https://github.com/Bogdanp/dramatiq/blob/master/dramatiq/broker.py#L34-L44
    DEFAULT_BROKER = 'dramatiq.brokers.rabbitmq:RabbitmqBroker'

    def __init__(self, app=None, broker_cls=DEFAULT_BROKER, name='dramatiq',
                 config_prefix=None, middleware=None):
        self.actors = []
        self.app = None
        self.broker_cls = broker_cls
        self.config_prefix = config_prefix or name.upper() + '_BROKER'
        self.name = name
        if middleware is None:
            middleware = [m() for m in default_middleware]
        self.middleware = middleware
        if app:
            self.init_app(app)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name)

    def init_app(self, app):
        if self.app is not None:
            warn(
                "%s is used by more than one flask application. "
                "Actor's context may be set incorrectly." % (self,),
                stacklevel=2,
            )
        self.app = app
        app.extensions['dramatiq-' + self.name] = self
        app.config.setdefault(self.config_prefix, self.broker_cls)
        cls = app.config[self.config_prefix]
        if isinstance(cls, str):
            cls = import_object(cls)
        kw = {}
        url = app.config.get(self.config_prefix + '_URL')
        if url:
            kw['url'] = url
        middleware = [AppContextMiddleware(app)] + self.middleware
        self.broker = cls(**kw, middleware=middleware)

        for actor in self.actors:
            actor.register(broker=self.broker)

    def actor(self, fn=None, **kw):
        # Substitude dramatiq.actor decorator to return a lazy wrapper. This
        # allow to register actors in extension before the broker is
        # effectively configured by init_app.

        def decorator(fn):
            lazy_actor = LazyActor(self, fn, kw)
            self.actors.append(lazy_actor)
            if self.app:
                lazy_actor.register(self.broker)
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

    def __call__(self, *a, **kw):
        return self.fn(*a, **kw)

    def __getattr__(self, name):
        if not self.actor:
            raise AttributeError(name)
        return getattr(self.actor, name)

    def register(self, broker):
        self.actor = register_actor(broker=broker, **self.kw)(self.fn)

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
@click.option('-Q', '--queues', type=str, default=None,
              metavar='QUEUES', show_default=True,
              help="listen to a subset of queues, comma separated")
@click.argument('broker_name', default='dramatiq')
@with_appcontext
def worker(processes, threads, queues, broker_name):
    """Run dramatiq workers.

    Setup Dramatiq with broker and task modules from Flask app.

    \b
    examples:
      # Run dramatiq with 1 thread per process.
      $ flask worker --threads 1

    \b
      # Listen only to the "foo" and "bar" queues.
      $ flask worker -Q foo,bar

    \b
      # Consuming from a specific broker
      $ flask worker mybroker
    """
    # Plugin for flask.commands entrypoint.
    #
    # Wraps dramatiq worker CLI in a Flask command. This is private API of
    # dramatiq.

    parser = dramatiq_argument_parser()

    # Set worker broker globally.
    needle = 'dramatiq-' + broker_name
    broker = current_app.extensions[needle].broker
    set_broker(broker)

    command = [
        "--processes", str(processes),
        "--threads", str(threads),
        # This module does not have broker local. Thus dramatiq fallbacks to
        # global broker.
        __name__,
    ]
    if current_app.config['DEBUG']:
        command.append("--verbose")
        if HAS_WATCHDOG:
            command += ["--watch", guess_code_directory(broker)]

    if queues:
        command += ["--queues"] + queues.split(",")
    args = parser.parse_args(command)
    dramatiq_worker(args)
