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


Customize Broker Creation
=========================

To customize broker instanciation, you may just point the ``DRAMATIQ_BROKER``
parameter to any callable factory. Dramatiq-pg call this parameter with
``middleware`` parameter and ``url`` if ``DRAMATIQ_BROKER_URL``. The callable
must return a Dramatiq broker instance.


.. code:: python

   def broker_factory(middleware, url=None):
       # Instanciate your broker here.
       broker = ...
       return broker

   ...

   DRAMATIQ_BROKER = 'myapp:broker_factory'


Using Dramatiq CLI
==================

You can still use ``dramatiq`` CLI instead of integrated ``flask worker``
command. Each ``Dramatiq`` object has a ``broker`` attribute pointing to
Dramatiq's broker instance. Ensure this object is importable by Dramatiq CLI:

.. code:: python

    app = create_app()
    broker = dramatiq.broker


Now call ``dramatiq`` CLI with ``some_module:broker`` as usual.


Schedule tasks with periodiq
============================

Flask-Dramatiq integrates periodiq with Flask, if periodiq is installed. You
need to add periodiq middleware before initializing extension.

.. code:: python

   from flask_dramatiq import Dramatiq
   from periodiq import PeriodiqMiddleware, cron

   dramatiq = Dramatiq()
   dramatiq.middleware.append(PeriodiqMiddleware())


   @dramatiq.actor(periodic=cron('0 9 * * *')
   def hello():
       print("Hello!")


Now, run periodiq scheduler process right from flask CLI:

.. code:: console

   $ flask periodiq
   ...
   I: Starting Periodiq, a simple scheduler for Dramatiq.
   I: Registered periodic actors:
   I:
   I:     m h dom mon dow          module:actor@queue
   I:     ------------------------ ------------------
   I:     0 9 * * *                app:hello@default
   I:
   I: Scheduling Actor(hello) at 2019-09-09T09:00:00+02:00.
   ...


That's it! Your Flask-Dramatiq workers will process scheduled messages.
