===========
 Changelog
===========

Version 0.8.0
=============

Released 2026 may the 28th.

- Support for dramatiq 2
- Add tox configuration

Version 0.7.0
=============

Released 2026 may the 28th.

- Migration of the repository to the GitHub pallets-eco organization.
- Support for Python 3.10 to 3.14

Version 0.6.0
=============

Released 2019 novembre the 6th.

- Integrate `Periodiq <https://gitlab.com/bersace/periodiq>`_.
- Logs managed actors on worker startup.


Version 0.4.1
=============

- Don't require watch dependencies at runtime.


Version 0.4.0
=============

Released 2019 march 27th.

- Automatic watch actor source file changes when DEBUG is set.
- Allow to replace default middlewares.


Version 0.3.2
=============

Released 2019 march 21th.

- Fix using StubBroker.
- Add unit test.
- Document with Sphinx and RTD.


Version 0.3.1
=============

Released 2019 march 21th.

- Fix register actor after init_app.


Version 0.3.0
=============

Released 2019 march 19th.

- Use ``-Q`` short option rather than ``-q`` to match ``dramatiq`` CLI options.
- Support multiple broker on the same Flask app with configuration key prefix.
- Allow to hard code broker class when declaring broker.
- Extend lazy object attribute access (e.g. actor_options, etc.).
- Warn on duplicate ``init_app`` calls.


Version 0.2.0
=============

Released 2019 march 7th. First public implementation.

- Configure broker class and URL from Flask ``app.config``.
- Support Application factory pattern.
- Tested on CI.
