#!/usr/bin/env python3
#
#      U S A G E
#
# This file is Flask custom script embedding route handlers, model, task and
# everything needed. example.py loads config.py script upon app creation.
# Ensure it fit your setup. Here is how to test this.
#
# Install dev dependencies:
#
#     uv sync --all-groups --all-extras
#
# Start RabbitMQ and Postgres:
#
#     docker-compose up -d
#
# Bootstrap the database:
#
#     ./example.py db upgrade
#
# You're now ready to run both webserver and background worker in two
# terminals:
#
#     FLASK_ENV=dev ./example.py run
#     FLASK_ENV=dev ./example.py worker
#
# Then use curl to trigger jobs and get job status. There is two kind of jobs:
# fast (sleeps .1s) and slow (sleeps 30s).
#
#     curl -X POST http://localhost:5000/job/fast
#     curl http://localhost/5000/job


import logging
import os
import pdb
import sys
import time

import click
from flask import Blueprint, Flask, jsonify, request
from flask.cli import FlaskGroup
from flask_dramatiq import Dramatiq
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from periodiq import PeriodiqMiddleware, cron


db = SQLAlchemy()
dramatiq = Dramatiq()
dramatiq.middleware.append(PeriodiqMiddleware())
logger = logging.getLogger(__name__)
example = Blueprint('example', 'example')
otherbroker = Dramatiq(name='other')


class Job(db.Model):
    __tablename__ = "jobs"

    TYPE_SLOW = "slow"
    TYPE_FAST = "fast"
    TYPES = TYPE_SLOW, TYPE_FAST

    STATUS_PENDING = "pending"
    STATUS_DONE = "done"
    STATUSES = STATUS_PENDING, STATUS_DONE

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(10), default=STATUS_PENDING, nullable=False)

    def process(self):
        if self.type == Job.TYPE_SLOW:
            time.sleep(30)
        elif self.type == Job.TYPE_FAST:
            time.sleep(.1)
        else:
            raise ValueError("Unknown job type.")

    def asdict(self):
        return dict(
            id=self.id,
            type=self.type,
            status=self.status,
        )


@otherbroker.actor(queue_name='otherq')
def other_job(job_id):
    process_job(job_id)


@dramatiq.actor
def process_job(job_id):
    job = Job.query.get(job_id)
    job.process()

    job.status = Job.STATUS_DONE
    db.session.add(job)
    db.session.commit()

    logger.info("Done job #%s.", job_id)


@dramatiq.actor(periodic=cron('* * * * *'))
def heartbeat():
    logger.info("Pulse.")


@example.route("/job/<job_id>")
def job(job_id):
    return jsonify(Job.query.get(job_id).asdict())


@example.route("/job/<type_>", methods=["POST"])
def job_post(type_):
    if type_ not in Job.TYPES:
        return jsonify(dict(message="Bad type.")), 400

    job = Job(type=type_)
    db.session.add(job)
    db.session.commit()

    broker = request.args.get('broker', 'default')
    if 'other' == broker:
        other_job.send(job.id)
    else:
        process_job.send(job.id)

    return jsonify(job.asdict())


@example.route("/job")
def jobs():
    jobs = Job.query.order_by(Job.id.desc()).all()
    return jsonify([j.asdict() for j in jobs])


def create_app():
    app = Flask(__name__)

    # Beware that app config must be loaded before you initialize Dramatiq
    # extension with app.
    app.config.from_pyfile('config.py', silent=True)

    db.init_app(app)
    Migrate(app, db)

    dramatiq.init_app(app)
    otherbroker.init_app(app)

    app.register_blueprint(example)

    return app


@click.group(cls=FlaskGroup, create_app=create_app)
def main(argv=sys.argv[1:]):
    pass


if '__main__' == __name__:
    command = sys.argv[1] if sys.argv[1:] else 'flask'
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(levelname)1.1s [{command}] %(message)s',
    )
    logger.setLevel(logging.DEBUG)
    logging.getLogger('periodiq').setLevel(logging.DEBUG)

    try:
        exit(main())
    except (pdb.bdb.BdbQuit, KeyboardInterrupt):
        logger.info("Interrupted.")
    except Exception:
        logger.exception('Unhandled error:')
        if sys.stdout.isatty():
            logger.debug("Dropping in debugger.")
            pdb.post_mortem(sys.exc_info()[2])

    exit(os.EX_SOFTWARE)
