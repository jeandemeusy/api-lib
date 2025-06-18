from typing import Optional

from src.api_lib import ApiLib
from src.http_method import HTTPMethod

from .objects import response


class HoprdApi(ApiLib):
    def __init__(self, url: str, token: str):
        super().__init__(url, token, "/api/v3/")

    async def address(self) -> Optional[response.Addresses]:
        return await self.request(HTTPMethod.GET, "account/address", resp_type=response.Addresses)

    async def node_info(self) -> Optional[response.Infos]:
        return await self.request(HTTPMethod.GET, "node/info", response.Infos)

    async def healthyz(self) -> bool:
        return await self.timeout_check_success("healthyz", 20)
