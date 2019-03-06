from subprocess import Popen, check_output
from time import sleep

import pytest
import requests


def http_wait(url):
    for _ in range(32):
        try:
            return requests.get(url)
        except requests.exceptions.ConnectionError:
            sleep(.1)
    else:
        raise Exception("Failed to start example.py on time.")


@pytest.fixture
def httpd():
    proc = Popen(["./example.py", "run"])

    try:
        yield proc
    finally:
        proc.kill()
        proc.wait()


@pytest.fixture
def worker():
    proc = Popen(["./example.py", "worker"])
    try:
        yield proc
    finally:
        proc.kill()
        proc.wait()


def test_help():
    out = check_output(["./example.py", "--help"])
    assert b"dramatiq workers" in out

    out = check_output(["./example.py", "worker", "--help"])
    assert b"--processes" in out


def test_fast(httpd, worker):
    http_wait("http://localhost:5000/job")

    res = requests.post("http://localhost:5000/job/fast")
    res = res.json()
    url = f"http://localhost:5000/job/{res['id']}"

    for _ in range(10):
        sleep(.2)
        res = requests.get(url)
        if 'done' == res.json()['status']:
            break
    else:
        raise Exception("Task not processed on time.")
