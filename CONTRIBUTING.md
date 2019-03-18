# Contributing to Flask-Dramatiq

Thanks for you attention to Flask-Dramatiq. Here are some hints on contributing
code to the project. Every contribution is welcome, not only code.


## Development with poetry

Flask-Dramatiq uses [poetry](https://poetry.eustace.io/) to manage the project,
the virtualenv and more. Once poetry is installed, it's pretty straightforward.

``` console
$ poetry install
$ poetry run ./example.py --help
```

A `docker-compose.yml` describes RabbitMQ and Postgres service to test with the
`example.py` script. This script is tested with pytest in real situation (no
mock, no stub).

``` console
$ poetry run pytest -x tests/func/
```

Submit patch through [GitLab merge request on
Flask-Dramatiq](https://gitlab.com/bersace/flask-dramatiq/merge_requests/new).


## Release Process

Just use poetry on `master`:

``` console
$ poetry version minor
$ poetry publish --build
$ git commit -a -m "Version X.Y"
$ git push git@gitlab.com:bersace/flask-dramatiq.git
```

You require access to [Flask-Dramatiq on
PyPI](https://pypi.org/project/flask-dramatiq/). Remember to update Changelog.
