import pytest
from aiohttp import ClientConnectorError

from api_lib.api_lib import ApiLib
from api_lib.method import Method

from .config.response import RequestFailure


@pytest.mark.asyncio
async def test_successful_call(api: ApiLib):
    status, resp = await api._call(Method.GET, "/always_succeed")
    assert status == 200
    assert isinstance(resp, dict)


@pytest.mark.asyncio
async def test_invalid_query_call(api: ApiLib):
    status, resp = await api._call(Method.GET, "/invalid_query")
    assert status == 404


@pytest.mark.asyncio
async def test_txt_call(api: ApiLib):
    status, resp = await api._call(Method.GET, "/read_me")
    assert status == 200
    assert isinstance(resp, str)


@pytest.mark.asyncio
async def test_exception_call_with_timeout(api: ApiLib):
    status, resp = await api._call_api_with_timeout(Method.GET, "/slow_endpoint", timeout=2)
    assert status is None
    assert resp is None


@pytest.mark.asyncio
async def test_api_returns_list(api: ApiLib):
    repos = await api.req(Method.GET, "/returns_list", list[dict])
    assert isinstance(repos, list)
    assert len(repos) > 0


@pytest.mark.asyncio
async def test_api_returns_text(api: ApiLib):
    readme = await api.req(Method.GET, "/read_me", str)
    assert isinstance(readme, str)
    assert len(readme) > 0


@pytest.mark.asyncio
async def test_unreachable_endpoint(api_not_reachable: ApiLib):
    with pytest.raises(ClientConnectorError):
        await api_not_reachable._call(Method.GET, "/always_succeed")


@pytest.mark.asyncio
async def test_return_state(api: ApiLib):
    status = await api.req(Method.GET, "/always_succeed", return_state=True)
    assert isinstance(status, int)


@pytest.mark.asyncio
async def test_no_return_type(api: ApiLib):
    result = await api.req(Method.GET, "/always_succeed", None)
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_timeout_check_success(api: ApiLib):
    result = await api.timeout_check_success("/always_fail", timeout=2)
    assert result is False

    result = await api.timeout_check_success("/always_succeed", timeout=2)
    assert result is True

    result = await api.timeout_check_success("/randomly_succeed", timeout=2)
    assert result is True


@pytest.mark.asyncio
async def test_status_failed_try_req(api: ApiLib):
    result = await api.try_req(Method.GET, "/invalid_query")
    assert result is None


@pytest.mark.asyncio
async def test_status_failed_req(api: ApiLib):
    with pytest.raises(RuntimeError):
        await api.req(Method.GET, "/invalid_query")


@pytest.mark.asyncio
async def test_default_fallback(api: ApiLib):
    result = await api.try_req(Method.GET, "/query_returns_an_error")

    assert result is not None
    assert isinstance(result, RequestFailure)
    assert result.error != "default fallback"


@pytest.mark.asyncio
async def test_authenticated_call(api: ApiLib, api_not_authenticated: ApiLib):
    status, resp = await api._call(Method.GET, "/authenticated")
    assert status == 200

    status, resp = await api_not_authenticated._call(Method.GET, "/authenticated")
    assert status == 401


@pytest.mark.asyncio
async def test_call_with_prefix(api_with_prefix: ApiLib):
    status, resp = await api_with_prefix._call(Method.GET, "/always_succeed")
    assert status == 200
    assert isinstance(resp, dict)
