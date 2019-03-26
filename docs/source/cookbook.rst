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
