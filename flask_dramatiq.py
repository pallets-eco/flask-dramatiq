"""

.. autoclass:: Dramatiq()


Periodiq helpers
================

Periodiq is a simple scheduler for Dramatiq. Theses attributes are exposed
in extension namespace as a graceful helper to access periodiq API.

.. attribute:: Dramatiq.cron
.. attribute:: Dramatiq.PeriodiqMiddleware

Exemple:

::

   from flask_dramatiq import Dramatiq

   dramatiq = Dramatiq(middleware=[PeriodiqMiddleware()])

   @dramatiq.actor(periodic=dramatiq.cron('0 * * * *'))
   def hourly():
       ...


See `periodiq project <https://gitlab.com/bersace/periodiq>`_ for details.

"""

import multiprocessing
import os.path
import sys
from importlib import import_module
from threading import local
from warnings import warn

import click
from dramatiq import actor as register_actor
from dramatiq import Middleware
from dramatiq import set_broker
from dramatiq.cli import CPUS
from dramatiq.cli import HAS_WATCHDOG
from dramatiq.cli import main as dramatiq_worker
from dramatiq.cli import make_argument_parser as dramatiq_argument_parser
from dramatiq.middleware import default_middleware
from flask import current_app
from flask import Flask
from flask.cli import with_appcontext


def guess_code_directory(broker):
    actor = next(iter(broker.actors.values()))
    modname, *_ = actor.fn.__module__.partition(".")
    mod = sys.modules[modname]
    return os.path.dirname(mod.__file__)


def import_object(path):
    # Implement setuptools entrypoint-like loading of object.
    modname, objname = path.split(":")
    mod = import_module(modname)
    try:
        return getattr(mod, objname)
    except AttributeError as err:
        raise ImportError(f"{path} does not exists.") from err


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

    def after_process_message(self, broker, message, *, result=None, exception=None):
        try:
            context = self.state.context
            context.pop(exception)
            del self.state.context
        except AttributeError:
            pass

    after_skip_message = after_process_message


class Dramatiq:
    """Flask extension bridging Dramatiq broker and Flask app.

    Dramatiq API is eager. Broker initialisation precede actor declaration.
    This breaks application factory pattern and other way to initialize
    configuration after import.

    This class enables lazy initialization of Dramatiq. Actual Dramatiq broker
    is instanciated only once Flask app is created.

    .. automethod:: actor
    .. automethod:: init_app
    """

    # Reuse same defaults as dramatiq. cf.
    # https://github.com/Bogdanp/dramatiq/blob/main/dramatiq/broker.py#L34-L44
    DEFAULT_BROKER = "dramatiq.brokers.rabbitmq:RabbitmqBroker"

    try:
        raise ImportError()
        from periodiq import cron
        from periodiq import PeriodiqMiddleware
    except ImportError:

        def cron(*_):
            pass

        PeriodiqMiddleware = None

    def __init__(
        self,
        app=None,
        broker_cls=DEFAULT_BROKER,
        name="dramatiq",
        config_prefix=None,
        middleware=None,
    ):
        """
        :app: Flask application if created. See :meth:`init_app`.

        :param broker_cls: Default Dramatiq broker class. Overridable by
            Flask configuration.

        :param name: Unique identifier for multi-broker app.

        :param config_prefix: Flask configuration option prefix for this
            broker. By default, it is derived from ``name`` parameter,
            capitalized.

        :param middleware: List of Dramatiq middleware instances to override
             Dramatiq defaults.

        Flask-Dramatiq always prepend a custom middleware to the middleware
        stack that setup Flask context. This way, every middleware can use
        Flask app context.

        """
        self.actors = []
        self.app = None
        self.broker_cls = broker_cls
        self.config_prefix = config_prefix or name.upper() + "_BROKER"
        self.name = name
        if middleware is None:
            middleware = [m() for m in default_middleware]
        self.middleware = middleware
        if app:
            self.init_app(app)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

    def init_app(self, app: Flask):
        """Initialize extension for one Flask application

        This method triggers Dramatiq broker instanciation and effective actor
        registration.

        """
        if self.app is not None:
            warn(
                f"{self} is used by more than one flask application. "
                "Actor's context may be set incorrectly.",
                stacklevel=2,
            )
        self.app = app
        app.extensions["dramatiq-" + self.name] = self
        app.config.setdefault(self.config_prefix, self.broker_cls)
        cls = app.config[self.config_prefix]
        if isinstance(cls, str):
            cls = import_object(cls)
        kw = {}
        url = app.config.get(self.config_prefix + "_URL")
        if url:
            kw["url"] = url
        middleware = [AppContextMiddleware(app)] + self.middleware
        self.broker = cls(**kw, middleware=middleware)

        for actor in self.actors:
            actor.register(broker=self.broker)

    def actor(self, fn=None, **kw):
        """Register a callable as Dramatiq actor.

        This decorator lazily register a callable as a Dramatiq actor. The
        actor can't be called before :meth:`init_app` is called.

        :param kw: Keywords argument passed to :func:`dramatiq.actor`.

        """
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


def format_actor(actor):
    return f"{actor.actor_name}@{actor.queue_name}"


class LazyActor:
    # Intermediate object that register actor on broker an call.

    def __init__(self, extension, fn, kw):
        self.extension = extension
        self.fn = fn
        self.kw = kw
        self.actor = None

    def __call__(self, *a, **kw):
        return self.fn(*a, **kw)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.fn.__module__}.{self.fn.__name__}>"

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


def list_managed_actors(broker, queues):
    queues = set(queues)
    all_actors = broker.actors.values()
    if not queues:
        return all_actors
    else:
        return [a for a in all_actors if a.queue_name in queues]


@click.command()
@click.option(
    "-v", "--verbose", default=0, count=True, help="turn on verbose log output"
)
@click.argument("broker_name", default="dramatiq")
@with_appcontext
def periodiq(verbose, broker_name):
    """Run periodiq scheduler.

    Setup Dramatiq with broker and task modules from Flask app.
    """
    try:
        import periodiq
    except ImportError:
        click.fail("Missing periodiq dependency.")

    needle = "dramatiq-" + broker_name
    broker = current_app.extensions[needle].broker
    set_broker(broker)

    command = [
        # This module does not have broker local. Thus dramatiq fallbacks to
        # global broker.
        __name__,
    ]

    if current_app.config["DEBUG"]:
        verbose = max(verbose, 1)

    command += verbose * ["-v"]
    parser = periodiq.make_argument_parser()
    args = parser.parse_args(command)
    periodiq.main(args)


@click.command()
@click.option(
    "-v", "--verbose", default=0, count=True, help="turn on verbose log output"
)
@click.option(
    "-p",
    "--processes",
    default=CPUS,
    metavar="PROCESSES",
    show_default=True,
    help="the number of worker processes to run",
)
@click.option(
    "-t",
    "--threads",
    default=8,
    metavar="THREADS",
    show_default=True,
    help="the number of worker treads per processes",
)
@click.option(
    "-Q",
    "--queues",
    type=str,
    default=None,
    metavar="QUEUES",
    show_default=True,
    help="listen to a subset of queues, comma separated",
)
@click.argument("broker_name", default="dramatiq")
@with_appcontext
def worker(verbose, processes, threads, queues, broker_name):
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

    # Python 3.14 changed multiprocessing default start method from 'fork'
    # to 'forkserver' on POSIX. flask-dramatiq sets the broker globally
    # then forks workers, which requires 'fork' to inherit broker state.
    if sys.platform != "win32" and sys.version_info >= (3, 14):
        multiprocessing.set_start_method("fork", force=True)

    parser = dramatiq_argument_parser()

    # Set worker broker globally.
    needle = "dramatiq-" + broker_name
    broker = current_app.extensions[needle].broker
    set_broker(broker)

    command = [
        "--processes",
        str(processes),
        "--threads",
        str(threads),
        # This module does not have broker local. Thus dramatiq fallbacks to
        # global broker.
        __name__,
    ]
    if current_app.config["DEBUG"]:
        verbose = max(1, verbose)
        if HAS_WATCHDOG:
            command += ["--watch", guess_code_directory(broker)]

    queues = queues.split(",") if queues else []
    if queues:
        command += ["--queues"] + queues
    command += verbose * ["-v"]
    args = parser.parse_args(command)

    current_app.logger.info("Able to execute the following actors:")
    for actor in list_managed_actors(broker, queues):
        current_app.logger.info("    %s.", format_actor(actor))

    dramatiq_worker(args)
