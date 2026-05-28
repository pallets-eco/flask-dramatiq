from subprocess import check_output
from subprocess import Popen
from time import monotonic
from time import sleep

import httpx
import pika
import pika.exceptions
import pytest

WORKER_READY_TIMEOUT = 30.0
POLL_INTERVAL = 0.1


def http_wait(url):
    for _ in range(32):
        try:
            return httpx.get(url)
        except httpx.ConnectError:
            sleep(0.1)
    else:
        raise Exception("Failed to start example.py on time.")


def wait_for_consumer(queue):
    params = pika.ConnectionParameters("localhost")
    deadline = monotonic() + WORKER_READY_TIMEOUT
    while monotonic() < deadline:
        try:
            conn = pika.BlockingConnection(params)
            try:
                ch = conn.channel()
                result = ch.queue_declare(queue=queue, passive=True)
                if result.method.consumer_count >= 1:
                    return
            finally:
                conn.close()
        except (pika.exceptions.AMQPError, OSError):
            pass
        sleep(POLL_INTERVAL)
    raise Exception(f"Worker for queue '{queue}' not ready on time.")


@pytest.fixture(scope="session")
def httpd():
    proc = Popen(["./example.py", "run"])

    try:
        yield proc
    finally:
        proc.kill()
        proc.wait()


def generic_worker(queues, broker_name="dramatiq"):
    proc = Popen(
        [
            "./example.py",
            "worker",
            "-vv",
            "-p",
            "1",
            "-t",
            "1",
            "-Q",
            ",".join(queues),
            broker_name,
        ]
    )
    try:
        for queue in queues:
            wait_for_consumer(queue)
        yield proc
    finally:
        proc.terminate()
        proc.wait()


@pytest.fixture(scope="session")
def worker():
    yield from generic_worker(["default"])


@pytest.fixture(scope="session")
def other_worker():
    yield from generic_worker(["otherq"], broker_name="other")


def test_help():
    out = check_output(["./example.py", "--help"])
    assert b"dramatiq workers" in out

    out = check_output(["./example.py", "worker", "--help"])
    assert b"--processes" in out


def test_fast(httpd, worker):
    http_wait("http://localhost:5000/job")

    res = httpx.post("http://localhost:5000/job/fast")
    res = res.json()
    url = f"http://localhost:5000/job/{res['id']}"

    for _ in range(10):
        sleep(0.2)
        res = httpx.get(url)
        if "done" == res.json()["status"]:
            break
    else:
        raise Exception("Task not processed on time.")


def test_other(httpd, other_worker):
    res = httpx.post("http://localhost:5000/job/fast?broker=other")
    res = res.json()
    url = f"http://localhost:5000/job/{res['id']}"

    for _ in range(10):
        sleep(0.2)
        res = httpx.get(url)
        if "done" == res.json()["status"]:
            break
    else:
        raise Exception("Task not processed on time.")
