from subprocess import Popen, check_output
from time import sleep

import pytest
import httpx


def http_wait(url):
    for _ in range(32):
        try:
            return httpx.get(url)
        except httpx.ConnectError:
            sleep(.1)
    else:
        raise Exception("Failed to start example.py on time.")


@pytest.fixture(scope='session')
def httpd():
    proc = Popen(["./example.py", "run"])

    try:
        yield proc
    finally:
        proc.kill()
        proc.wait()


def generic_worker(*args):
    proc = Popen([
        "./example.py", "worker", "-vv", "-p", "1", "-t", "1"] + list(args))
    sleep(.5)
    try:
        yield proc
    finally:
        proc.terminate()
        proc.wait()


@pytest.fixture(scope='session')
def worker():
    yield from generic_worker("-Q", "default")


@pytest.fixture(scope='session')
def other_worker():
    yield from generic_worker("-Q", "otherq", "other")


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
        sleep(.2)
        res = httpx.get(url)
        if 'done' == res.json()['status']:
            break
    else:
        raise Exception("Task not processed on time.")


def test_other(httpd, other_worker):
    res = httpx.post("http://localhost:5000/job/fast?broker=other")
    res = res.json()
    url = f"http://localhost:5000/job/{res['id']}"

    for _ in range(10):
        sleep(.2)
        res = httpx.get(url)
        if 'done' == res.json()['status']:
            break
    else:
        raise Exception("Task not processed on time.")
