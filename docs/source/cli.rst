===============
 CLI Reference
===============


.. program:: flask worker

Run a dramatiq worker
=====================

Flask-Dramatiq extension provides a flask command to configure and execute
Dramatiq worker processes from Flask CLI. The :program:`worker` command has the
same options as Dramatiq worker command.


::

   $ flask worker --help
   Usage: flask worker [OPTIONS] [BROKER_NAME]

   Run dramatiq workers.

   Setup Dramatiq with broker and task modules from Flask app.

   examples:
       # Run dramatiq with 1 thread per process.
       $ flask worker --threads 1

       # Listen only to the "foo" and "bar" queues.
       $ flask worker -Q foo,bar

       # Consuming from a specific broker
       $ flask worker mybroker

   Options:
   -v, --verbose              turn on verbose log output  [x>=0]
   -p, --processes PROCESSES  the number of worker processes to run  [default:
                              8]
   -t, --threads THREADS      the number of worker treads per processes
                              [default: 8]
   -Q, --queues QUEUES        listen to a subset of queues, comma separated
   --help                     Show this message and exit.


.. program:: flask periodiq

Run periodiq scheduler
======================

The periodiq scheduler is also available as a flask command named `periodiq`.

::

   $ flask periodiq --help
   Usage: flask periodiq [OPTIONS] [BROKER_NAME]

   Run periodiq scheduler.

   Setup Dramatiq with broker and task modules from Flask app.

   Options:
   -v, --verbose  turn on verbose log output  [x>=0]
   --help         Show this message and exit.
