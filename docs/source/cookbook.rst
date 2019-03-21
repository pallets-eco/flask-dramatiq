==========
 Cookbook
==========

Here are some recipes for more usage of Flask-Dramatiq.

Add middleware
==============

The ``Dramatiq`` object expose the broker instance as ``broker`` attribute, once
the app is initialized. Thus you can add middleware either after a
``Dramatiq(app)`` or ``dramatiq.init_app(app)`` call. Here is a sample.

.. code:: python

   def create_app():
       app = Flask(__name__)
       dramatiq.init_app(app)
       dramatiq.broker.add_middleware(...)


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
