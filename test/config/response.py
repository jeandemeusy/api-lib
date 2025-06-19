from dataclasses import field

from src.objects.response import APIfield, APIobject, JsonResponse, MetricResponse


@APIobject
class Repository(JsonResponse):
    name: str = APIfield()
    fullname: str = APIfield("full_name")


@APIobject
class User(JsonResponse):
    login: str = APIfield()
    name: str = APIfield()
    disk_usage: int = APIfield()
    disk_space_limit: int = APIfield("plan/space")


@APIobject
class ResponseClass(JsonResponse):
    field: str = APIfield()
    path_field: str = APIfield(path="path/to/field")
    default_field: str = APIfield(default="default_value")


@APIobject
class MetricResponseClass(MetricResponse):
    metric_one: float = field()
    metric_two: dict = field(metadata={"labels": ["label_name"]})
    metric_three: int = field()
