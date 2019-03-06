# // Flask-Dramatiq //

Flask-Dramatiq plugs Dramatiq in your Flask application.

## Features

- Configure Dramatiq from Flask configuration.
- Ensure Flask app is available to Dramatiq actor.
- Enable [Flask Application factory](http://flask.pocoo.org/docs/dev/tutorial/factory/).
- Add `worker` command to Flask CLI.


## Installation and Usage

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
```

A complete flask app is available in project source tree
[example.py](https://gitlab.com/bersace/flask-dramatiq/blob/master/example.py).


## Credit and Support

Feel free to open an issue or suggest a merge request on [Gitlab project
page](https://gitlab.com/bersace/flask-dramatiq). Contribution welcome!

The project is based on
[Bogdanp/flask_dramatiq_example](https://github.com/Bogdanp/flask_dramatiq_example).
