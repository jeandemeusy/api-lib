from dataclasses import dataclass

from api_lib.objects.request import APIfield, RequestData


@dataclass
class Pagination(RequestData):
    per_page: str
    page: str


@dataclass
class RequestClass(RequestData):
    field: str
    path_field: str = APIfield(api_key="other_key")
    default_field: str = APIfield(default="default_value")
