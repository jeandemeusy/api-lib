from .hoprd_api import HoprdApi


def test_api_lib():
    _ = HoprdApi("http://localhost:8080", "test_token")
