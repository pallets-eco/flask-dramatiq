# Changelog

## [master] - Unreleased

- Use `-Q` short option rather than `-q` to match `dramatiq` CLI options.
- Support multiple broker on the same Flask app with configuration key prefix.
- Allow to hard code broker class when declaring broker.
- Extend lazy object attribute access (e.g. actor_options, etc.).
- Warn on duplicate `init_app` calls.


## [0.2.0] - 2019 March 7

First public implementation.

- Configure broker class and URL from Flask `app.config`.
- Support Application factory pattern.
- Tested on CI.
