import pytest
from dotenv import load_dotenv

from api_lib.headers.authorization import Bearer

from .config.github_api import GithubAPI
from .config.request import RequestClass

load_dotenv()


@pytest.fixture
def gh_api():
    return GithubAPI("https://api.github.com", Bearer(env_var="GITHUB_TOKEN"))


@pytest.fixture
def request_object():
    return RequestClass("test_value", "path_value")
