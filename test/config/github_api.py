from typing import Optional

from src.api_lib import ApiLib
from src.headers import Header
from src.headers.accept import AcceptGithub
from src.method import Method

from .response import Repository, User


class GithubAPI(ApiLib):
    headers: list[Header] = [AcceptGithub()]

    async def user(self) -> User:
        return await self.req(Method.GET, "/user", User)

    async def followers(self, username: Optional[str] = None) -> list[User]:
        path = f"/users/{username}/followers" if username else "/user/followers"
        return await self.req(Method.GET, path, list[User])

    async def following(self, username: Optional[str] = None) -> list[User]:
        path = f"/users/{username}/following" if username else "/user/following"
        return await self.req(Method.GET, path, list[User])

    async def repositories(self, organization: str) -> list[Repository]:
        return await self.req(Method.GET, f"/orgs/{organization}/repos", list[Repository])
