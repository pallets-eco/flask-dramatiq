# Contributing to Flask-Dramatiq

Thanks for you attention to Flask-Dramatiq. Here are some hints on contributing
code to the project. Every contribution is welcome, not only code.


## Development with uv

Flask-Dramatiq uses [uv](https://docs.astral.sh/uv/) to manage the project and
the virtualenv. Once uv is installed, it's pretty straightforward.

``` console
$ uv sync --group dev
$ uv run ./example.py --help
```

A `docker-compose.yml` describes RabbitMQ and Postgres service to test with the
`example.py` script. This script is tested with pytest in real situation (no
mock, no stub).

``` console
$ uv run pytest -x tests/func/
```

Submit patch through [GitHub pull request on
Flask-Dramatiq](https://github.com/pallets-eco/flask-dramatiq/pulls/new).


## Release Process

Bump version in `pyproject.toml`, then on `master`:

``` console
$ uv build
$ uv publish
$ git commit -a -m "Version X.Y"
$ git push git@github.com:pallets-eco/flask-dramatiq.git
```

You require access to [Flask-Dramatiq on
PyPI](https://pypi.org/project/flask-dramatiq/). Remember to update Changelog.
