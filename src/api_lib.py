import asyncio
import logging
from typing import Optional, Union

import aiohttp

from .header import BearerToken
from .http_method import HTTPMethod
from .objects import RequestData, Response

logger = logging.getLogger("api-lib")


class ApiLib:
    def __init__(self, url: str, token: str, prefix: Optional[str] = None):
        self.host = url
        self.token = BearerToken(token)
        self.prefix = "" if prefix is None else prefix

    async def __call(
        self,
        method: HTTPMethod,
        endpoint: str,
        data: Optional[RequestData] = None,
        use_api_prefix: bool = True,
    ):
        logger.debug(
            "Hitting API",
            {
                "host": self.host,
                "method": method.value,
                "endpoint": endpoint,
                "data": getattr(data, "as_dict", {}),
            },
        )

        try:
            headers = {"Content-Type": "application/json"}
            async with aiohttp.ClientSession(headers=self.token.header) as s:
                async with getattr(s, method.value)(
                    url=f"{self.host}{self.prefix if use_api_prefix else '/'}{endpoint}",
                    json={} if data is None else data.as_dict,
                    headers=headers,
                ) as res:
                    try:
                        data = await res.json()
                    except Exception:
                        data = await res.text()

                    return (res.status // 200) == 1, data
        except OSError as err:
            logger.error(
                "OSError while doing an API call",
                {
                    "error": str(err),
                    "host": self.host,
                    "method": method.value,
                    "endpoint": endpoint,
                },
            )

        except Exception as err:
            logger.error(
                "Exception while doing an API call",
                {
                    "error": str(err),
                    "host": self.host,
                    "method": method.value,
                    "endpoint": endpoint,
                },
            )

        return (False, None)

    async def __call_api_with_timeout(
        self,
        method: HTTPMethod,
        endpoint: str,
        data: Optional[RequestData] = None,
        timeout: int = 90,
        use_api_prefix: bool = True,
    ) -> tuple[bool, Optional[object]]:
        backoff = 0.5
        while True:
            try:
                result = await asyncio.wait_for(
                    asyncio.create_task(self.__call(method, endpoint, data, use_api_prefix)),
                    timeout=timeout,
                )
            except aiohttp.ClientConnectionError as err:
                backoff *= 2
                logger.exception(
                    "ClientConnection exception while doing an API call.",
                    {
                        "error": str(err),
                        "host": self.host,
                        "method": method.value,
                        "endpoint": endpoint,
                        "backoff": backoff,
                    },
                )
                if backoff > 10:
                    return (False, None)
                await asyncio.sleep(backoff)

            except asyncio.TimeoutError as err:
                logger.error(
                    "Timeout error while doing an API call",
                    {
                        "error": str(err),
                        "host": self.host,
                        "method": method.value,
                        "endpoint": endpoint,
                    },
                )
                return (False, None)
            else:
                return result

    async def req(
        self,
        method: HTTPMethod,
        path: str,
        resp_type: Optional[Response] = None,
        data: Optional[RequestData] = None,
        use_api_prefix: bool = True,
        return_state: bool = False,
        timeout: int = 90,
    ) -> Optional[Union[Response, dict]]:
        is_ok, r = await self.__call_api_with_timeout(
            method, path, data, timeout=timeout, use_api_prefix=use_api_prefix
        )

        if return_state:
            return is_ok

        if not is_ok:
            return None

        if resp_type is None:
            return r

        return resp_type(r)  # ty: ignore[call-non-callable]

    async def safe_req(
        self,
        method: HTTPMethod,
        path: str,
        resp_type: Optional[Response] = None,
        data: Optional[RequestData] = None,
        use_api_prefix: bool = True,
        return_state: bool = False,
        timeout: int = 90,
    ) -> Union[Response, dict]:
        resp = await self.req(
            method,
            path,
            data,
            resp_type,
            use_api_prefix,
            return_state,
            timeout,
        )

        if resp is None:
            logger.error(
                "API request failed",
                {
                    "method": method.value,
                    "path": path,
                    "data": getattr(data, "as_dict", {}),
                },
            )
            raise RuntimeError("API request failed")
        return resp

    async def timeout_check_success(self, path: str, timeout: int = 20):
        try:
            is_ok = await asyncio.wait_for(self.__check_url(path), timeout=timeout)
        except asyncio.TimeoutError:
            return False
        except Exception:
            return False
        else:
            return is_ok

    async def __check_url(self, path: str, use_api_prefix: bool = False):
        while True:
            try:
                return await self.req(
                    HTTPMethod.GET,
                    path,
                    use_api_prefix=use_api_prefix,
                    return_state=True,
                    timeout=None,
                )
            except Exception:
                await asyncio.sleep(0.25)
