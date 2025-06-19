import os

import pytest

from .config.github_api import GithubAPI


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("CI", "false") == "true", reason="Skipping on CI")
async def test_simple_api(gh_api: GithubAPI):
    user = await gh_api.user()

    assert user.login != ""
    assert user.name != ""
    assert user.disk_usage >= 0
    assert user.disk_space_limit > 0


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("CI", "false") == "true", reason="Skipping on CI")
async def test_api_returns_list(gh_api: GithubAPI):
    repos = await gh_api.repositories("astral-sh")
    assert isinstance(repos, list)
    assert len(repos) > 0
