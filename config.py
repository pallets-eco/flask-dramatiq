# flake8: noqa
import os

DRAMATIQ_BROKER = 'dramatiq.brokers.rabbitmq:RabbitmqBroker'
DRAMATIQ_BROKER_URL = os.environ.get('BROKER_URL', 'amqp://rabbitmq.flask-dramatiq.docker/')

PGHOST = os.environ.get('PGHOST', 'postgres.flask-dramatiq.docker')
PGUSER = os.environ.get('PGUSER', 'postgres')
PGPASSWORD = os.environ.get('PGPASSWORD', '')
PGDATABASE = os.environ.get('PGDATABASE', PGUSER)

SQLALCHEMY_DATABASE_URI = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}/{PGDATABASE}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
