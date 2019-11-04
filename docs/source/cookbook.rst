==========
 Cookbook
==========

Here are some recipes for more usage of Flask-Dramatiq.

Setup middlewares
=================

The ``Dramatiq`` constructor accepts ``middleware`` argument to overwrite
default middlewares. If you need to configure middleware from Flask
configuration, you'd better instanciate and add middleware once app is loaded
and configured. ``Dramatiq`` object exposes the broker instance as ``broker``
attribute once app is initialized. Thus you can add middleware either after a
``Dramatiq(app)`` or ``dramatiq.init_app(app)`` call. Here is a sample.

.. code:: python

   dramatiq = Dramatiq(middleware=[...])

   def create_app():
       app = Flask(__name__)
       dramatiq.init_app(app)
       dramatiq.broker.add_middleware(..., after=...)

All middleware can access ``current_app`` thread local as app context is
initialized before any middlewares.


Multiple brokers
================

You may need multiple broker, e.g. by associating a broker with a blueprint.
Flask-Dramatiq supports this. Give other broker a name and run a dedicated
worker for it.

.. code:: python

   bluebroker = Dramatiq(name='bluebroker')

   @bluebroker.actor
   def myactor():
       ...

The ``bluebroker`` has a dedicated prefix for configuration options:

.. code:: python

   BLUEBROKER_URL = 'rabbitmq:///…'


Now run a dedicated worker process for this broker:

.. code:: console

   $ flask worker bluebroker


Using Dramatiq CLI
==================

You can still use ``dramatiq`` CLI instead of integrated ``flask worker``
command. Each ``Dramatiq`` object has a ``broker`` attribute pointing to
Dramatiq's broker instance. Ensure this object is importable by Dramatiq CLI:

.. code:: python

    app = create_app()
    broker = dramatiq.broker


Now call ``dramatiq`` CLI with ``some_module:broker`` as usual.


Using a Periodiq Scheduler
==========================

Once you have a pub/sub in your application, you may want to have something
publishing message on a timely manner, this is Scheduler. Dramatiq does not have
a built-in scheduler. There is plenty of solution and on of those is `periodiq
<https://gitlab.com/bersace/periodiq>`_ .

Periodiq provides a new actor option called ``periodic`` (without ``q``)
accepting a timer specification. The ``cron`` function instanciate a timer
specification using the well-known crontab(5) format. Finally, Periodiq ships a
light dedicated service idling until a message needs publishing.

Flask-Dramatiq integrates Periodiq **if installed**. Like Flask-SQLAlchemy does
with SQLAlchmy, Flask-Dramatiq imports periodiq common API in extension its own
namespace. See the following example:

.. code:: python

   from flask_dramatiq import Dramatiq

   dramatiq = Dramatiq()
   dramatiq.add_middleware(dramatiq.PeriodiqMiddleware())


   @dramatiq.actor(periodiq=dramatiq.cron('@hourly'))
   def my_hourly_chores():
        pass


   ...

   def create_app():
       app = ...
       dramatiq.init_app(app)
       return app

Finaly, run the scheduler with your Flask configured broker by running ``flask
periodiq``.

.. code:: console

   $ FLASK_APP=wsgi flask scheduler

That's it. See ``flask periodiq --help`` for more.
