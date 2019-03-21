![Flask-Dramatiq](https://gitlab.com/bersace/flask-dramatiq/raw/master/docs/logo-horizontal.png?inline=false)

Flask-Dramatiq plugs [Dramatiq](https://dramatiq.io) task queue in your
[Flask](https://flask.pocoo.org) web application.

## // Features // 

- Configure Dramatiq from Flask configuration.
- Ensure Flask app is available to Dramatiq actor.
- Add `worker` command to Flask CLI.
- Enable [Flask Application factory](http://flask.pocoo.org/docs/dev/tutorial/factory/).
- Handle multiple brokers with configurable prefix.

Full documentation at
[flask-dramatiq.readthedocs.io](https://flask-dramatiq.readthedocs.io).


## // Installation and Usage //

Flask-Dramatiq is licensed under BSD-3-Clause. Add `flask-dramatiq` to your
project:

``` console
$ poetry add flask-dramatiq
```

Then use `Dramatiq` object as a regular Flask extension:

``` python
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
```

Flask-Dramatiq adds two configuration keys:

- `DRAMATIQ_BROKER`, points to broker class like
  `dramatiq.brokers.rabbitmq.RabbitmqBroker` or
  `dramatiq.brokers.redis.RedisBroker`.
- `DRAMATIQ_BROKER_URL` is passed as `url` keyword argument to broker class.

Now run worker program to consume messages and execute tasks in the background:

``` console
$ flask worker --processes=1
```

A complete flask app is available in project source tree
[example.py](https://gitlab.com/bersace/flask-dramatiq/blob/master/example.py).


## // Credit and Support //

Feel free to open an issue or suggest a merge request on [Gitlab project
page](https://gitlab.com/bersace/flask-dramatiq). Contribution welcome!

The project is based on
[Bogdanp/flask_dramatiq_example](https://github.com/Bogdanp/flask_dramatiq_example).
