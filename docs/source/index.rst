.. Flask-Dramatiq documentation master file, created by
   sphinx-quickstart on Wed Mar 20 15:46:38 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

################
 Flask-Dramatiq
################

(:doc:`cookbook`, :doc:`changelog`, `Source Code`_)

.. _Source Code: https://gitlab.com/bersace/flask-dramatiq

| |PyPI| |License| |CI|

Welcome to Flask-Dramatiq's documentation. Flask-Dramatiq is a Flask_ extensions
to bridge Dramatiq_ task queue in your web app.

Features
========

- Setup Dramatiq from Flask configuration.
- Ensure Flask app is available to Dramatiq actor.
- Add ``worker`` command to Flask CLI.
- Enable `Flask Application factory
  <http://flask.pocoo.org/docs/dev/tutorial/factory/>`_.
- Handle multiple brokers with configurable prefix.
- Automatic code reload on change if ``DEBUG`` is set.


Get started
===========

Flask-Dramatiq is licensed under BSD-3-Clause. Add ``flask-dramatiq`` package to
your project:

.. code:: console

    $ poetry add flask-dramatiq


Then use ``Dramatiq`` object as a regular Flask extension. The ``Dramatiq``
object replaces the ``dramatiq`` module.

.. code:: python

   from flask import Flask
   from flask_dramatiq import Dramatiq

   app = Flask(__name__)
   dramatiq = Dramatiq(app)

   @dramatiq.actor()
   def my_actor():
       ...

   @app.route("/")
   def myhandler():
       my_actor.send()


Flask-Dramatiq adds two configuration keys:

- ``DRAMATIQ_BROKER``, points to broker class like
  ``dramatiq.brokers.rabbitmq:RabbitmqBroker`` or
  ``dramatiq.brokers.redis:RedisBroker``.
- ``DRAMATIQ_BROKER_URL`` is passed as ``url`` keyword argument to Dramatiq
  broker class.

Now run worker command to consume messages and execute tasks in the background:

.. code:: console

   $ flask worker --processes=1

That's it! A complete flask app is available in project source tree `example.py
<https://gitlab.com/bersace/flask-dramatiq/blob/master/example.py>`_


Table of contents
=================

.. toctree::
   :maxdepth: 2

   cookbook
   api
   cli
   changelog
   Source Code <https://gitlab.com/bersace/flask-dramatiq>

.. _Dramatiq: https://dramatiq.io/
.. _Flask: https://flask.pocoo.org/

.. |CI| image:: https://gitlab.com/bersace/flask-dramatiq/badges/master/pipeline.svg
   :target: https://gitlab.com/bersace/flask-dramatiq/-/pipelines
   :alt: Continuous Integration report

.. |PyPI| image:: https://img.shields.io/pypi/v/flask-dramatiq.svg
   :target: https://pypi.python.org/pypi/flask-dramatiq
   :alt: Version on PyPI

.. |License| image:: https://img.shields.io/pypi/l/flask-dramatiq.svg
   :alt: BSD-3-Clause
