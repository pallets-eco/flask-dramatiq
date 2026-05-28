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

Releases are published automatically by the [`Publish` GitHub Actions
workflow](.github/workflows/publish.yml) when a `vX.Y.Z` tag is pushed. The
workflow builds the distributions with `uv`, uploads them to PyPI using
[trusted publishing](https://docs.pypi.org/trusted-publishers/), and creates a
GitHub Release with the generated artifacts.

To cut a new release:

1. Bump the version in `pyproject.toml` and update the changelog.
2. Commit and push to `main`:

   ``` console
   $ git commit -a -m "Version X.Y.Z"
   $ git push origin main
   ```

3. Create and push the matching tag:

   ``` console
   $ git tag vX.Y.Z
   $ git push origin vX.Y.Z
   ```
