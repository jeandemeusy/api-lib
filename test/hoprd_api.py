from src.api_lib import ApiLib
from src.http_method import HTTPMethod

from .objects import response


class HoprdApi(ApiLib):
    def __init__(self, url: str, token: str):
        super().__init__(url, token, "/api/v3/")

    async def address(self) -> response.Addresses:
        return await self.safe_req(HTTPMethod.GET, "account/address", response.Addresses)

    async def node_info(self) -> response.Infos:
        return await self.safe_req(HTTPMethod.GET, "node/info", response.Infos)

    async def healthyz(self) -> bool:
        return await self.timeout_check_success("healthyz", 20)
