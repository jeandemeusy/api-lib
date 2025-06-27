import asyncio
import logging
from typing import Any, Callable, Iterable, Optional, Tuple, Union, get_args, get_origin

import aiohttp

from .headers import Authorization, Header
from .method import Method
from .objects import RequestData, Response

logger = logging.getLogger("api-lib")


class ApiLib:
    """
    Main API client class for making asynchronous HTTP requests with custom headers and authentication.

    Attributes:
        headers (list[Header]): List of default headers to include in requests.
        host (str): Base URL for the API.
        token (Optional[Authorization]): Optional authorization header.
        prefix (str): Optional prefix for API endpoints.
    """

    headers: list[Header] = []

    def __init__(
        self,
        url: str,
        token: Optional[Authorization] = None,
        prefix: Optional[str] = None,
    ):
        """
        Initialize the ApiLib client.

        Args:
            url (str): Base URL for the API.
            token (Optional[Authorization]): Optional authorization header.
            prefix (Optional[str]): Optional prefix for API endpoints.
        """
        self.host = url
        self.token = token
        self.prefix = prefix or ""
        self._headers = {k: v for h in (self.headers or []) for k, v in h.header.items()}

    async def _call(
        self,
        method: Method,
        path: str,
        data: Optional[RequestData] = None,
        use_api_prefix: bool = True,
    ):
        """
        Internal method to perform an asynchronous HTTP request.

        Args:
            method (Method): HTTP method to use.
            path (str): API endpoint path.
            data (Optional[RequestData]): Request data to send.
            use_api_prefix (bool): Whether to use the API prefix.

        Returns:
            tuple: A tuple containing the response status and data.
        """
        logger.debug(
            "Hitting API",
            {
                "host": self.host,
                "method": method.value,
                "path": path,
                "data": getattr(data, "as_dict", {}),
            },
        )
        async with aiohttp.ClientSession(headers=getattr(self.token, "header", {})) as s:
            async with getattr(s, method.value)(
                url=f"{self.host}{self.prefix if use_api_prefix else ''}{path}",
                json={} if data is None else data.as_dict,
                headers=self._headers,
            ) as res:
                try:
                    data: dict = await res.json()
                except aiohttp.ContentTypeError:
                    data: str = await res.text()
                except Exception as e:
                    raise e

                return res.status, data

    async def _call_api_with_timeout(
        self,
        method: Method,
        path: str,
        data: Optional[RequestData] = None,
        timeout: int = 90,
        use_api_prefix: bool = True,
    ) -> tuple[Optional[int], Optional[object]]:
        """
        Internal method to perform an asynchronous HTTP request with a timeout.

        Args:
            method (Method): HTTP method to use.
            path (str): API endpoint path.
            data (Optional[RequestData]): Request data to send.
            timeout (int): Timeout in seconds.
            use_api_prefix (bool): Whether to use the API prefix.

        Returns:
            tuple: A tuple containing the response status and data, or (None, None) on error.
        """
        while True:
            try:
                return await asyncio.wait_for(
                    asyncio.create_task(self._call(method, path, data, use_api_prefix)),
                    timeout=timeout,
                )
            except aiohttp.ClientConnectionError as err:
                logger.exception(
                    "ClientConnection exception while doing an API call.",
                    {
                        "error": str(err),
                        "host": self.host,
                        "method": method.value,
                        "path": path,
                    },
                )
            except asyncio.TimeoutError as err:
                logger.error(
                    "Timeout error while doing an API call",
                    {
                        "error": str(err),
                        "host": self.host,
                        "method": method.value,
                        "path": path,
                    },
                )
            except OSError as err:
                logger.error(
                    "OSError while doing an API call",
                    {
                        "error": str(err),
                        "host": self.host,
                        "method": method.value,
                        "path": path,
                    },
                )
            except Exception as err:
                logger.error(
                    f"Exception while doing an API call {err}",
                    {
                        "error": str(err),
                        "host": self.host,
                        "method": method.value,
                        "path": path,
                    },
                )
            return (None, None)

    async def try_req(
        self,
        method: Method,
        path: str,
        resp_type: Optional[Callable] = None,
        data: Optional[RequestData] = None,
        use_api_prefix: bool = True,
        return_state: bool = False,
        timeout: int = 90,
    ) -> Optional[Union[Response, dict]]:
        """
        Attempt to perform an API request and deserialize the response.

        Args:
            method (Method): HTTP method to use.
            path (str): API endpoint path.
            resp_type (Optional[Callable]): Response type or model to deserialize the response data.
            data (Optional[RequestData]): Request data to send.
            use_api_prefix (bool): Whether to use the API prefix.
            return_state (bool): Whether to return the response status.
            timeout (int): Timeout in seconds.

        Returns:
            Optional[Union[Response, dict]]: The deserialized response data, or None on error.
        """
        status, r = await self._call_api_with_timeout(
            method, path, data, timeout=timeout, use_api_prefix=use_api_prefix
        )

        if return_state:
            return status // 100 == 2  # Return True if status is a 2xx response

        if status // 100 != 2:  # Not a 2xx response
            return None

        if resp_type is None:
            return r

        origin: Optional[Any] = get_origin(resp_type)
        args: Tuple[Optional[Any], ...] = get_args(resp_type)

        if origin and issubclass(origin, Iterable) and args:
            return [args[0](item) for item in r]
        else:
            return resp_type(r)  # ty: ignore[call-non-callable]

    async def req(
        self,
        method: Method,
        path: str,
        resp_type: Optional[Callable] = None,
        data: Optional[RequestData] = None,
        use_api_prefix: bool = True,
        return_state: bool = False,
        timeout: int = 90,
    ) -> Union[Response]:
        """
        Perform an API request and return the response.

        Args:
            method (Method): HTTP method to use.
            path (str): API endpoint path.
            resp_type (Optional[Callable]): Response type or model to deserialize the response data.
            data (Optional[RequestData]): Request data to send.
            use_api_prefix (bool): Whether to use the API prefix.
            return_state (bool): Whether to return the response status.
            timeout (int): Timeout in seconds.

        Raises:
            RuntimeError: If the API request fails.

        Returns:
            Union[Response]: The deserialized response data.

        """
        resp = await self.try_req(
            method,
            path,
            resp_type,
            data,
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

    async def timeout_check_success(self, path: str, timeout: int = 20) -> bool:
        """
        Check if the API endpoint is reachable and responds successfully within the timeout.

        Args:
            path (str): API endpoint path.
            timeout (int): Timeout in seconds.

        Returns:
            bool: True if the endpoint is reachable and responds with a 2xx status, False otherwise.
        """
        try:
            is_ok = await asyncio.wait_for(self.__check_url(path), timeout=timeout)
        except (asyncio.TimeoutError, Exception):
            return False
        else:
            return is_ok

    async def __check_url(self, path: str, use_api_prefix: bool = False) -> bool:
        """
        Internal method to check the availability of an API endpoint.

        Args:
            path (str): API endpoint path.
            use_api_prefix (bool): Whether to use the API prefix.

        Returns:
            bool: True if the endpoint is available, False otherwise.
        """
        is_ok = False
        while not is_ok:
            try:
                is_ok = await self.req(
                    Method.GET,
                    path,
                    use_api_prefix=use_api_prefix,
                    return_state=True,
                    timeout=None,
                )
            except Exception:
                await asyncio.sleep(0.25)
            else:
                if is_ok:
                    return is_ok
