import time
from multiprocessing import Process

import pytest

from api_lib.api_lib import ApiLib
from api_lib.headers.authorization import Bearer

from .config.response import RequestFailure
from .config.rest_api import run_server

REST_API_HOST: str = "localhost"
REST_API_PORT: int = 5001
REST_API_TOKN: str = "test_token"


@pytest.fixture
def api():
    return ApiLib(f"http://{REST_API_HOST}:{REST_API_PORT}", Bearer(REST_API_TOKN)).with_failure_fallback(
        RequestFailure
    )


@pytest.fixture
def api_not_reachable():
    return ApiLib(f"http://{REST_API_HOST}:{REST_API_PORT+1}", Bearer(REST_API_TOKN))


@pytest.fixture
def api_not_authenticated():
    return ApiLib(f"http://{REST_API_HOST}:{REST_API_PORT}")


@pytest.fixture
def api_with_prefix():
    return ApiLib(f"http://{REST_API_HOST}:{REST_API_PORT}", Bearer(REST_API_TOKN)).with_api_prefix("/api/v1")


@pytest.fixture(scope="session", autouse=True)
def rest_server():
    proc = Process(
        target=run_server,
        args=(REST_API_HOST, REST_API_PORT),
        daemon=True,
    )
    proc.start()
    time.sleep(0.1)  # wait for server to start
    yield
    proc.terminate()
