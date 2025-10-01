from api_lib.objects.response import (
    APIfield,
    APImetric,
    APIobject,
    JsonResponse,
    MetricResponse,
)


@APIobject
class RequestFailure(JsonResponse):
    error: str = APIfield(default="undefined error")
    status: str = APIfield(default="undefined failure")


@APIobject
class Repository(JsonResponse):
    name: str
    fullname: str = APIfield("full_name")


@APIobject
class User(JsonResponse):
    login: str
    name: str
    disk_usage: int
    disk_space_limit: int = APIfield("plan/space")


@APIobject
class ResponseClass(JsonResponse):
    field: str
    path_field: str = APIfield(path="path/to/field")
    default_field: str = APIfield(default="default_value")


@APIobject
class ResponseWithList(JsonResponse):
    this_list: list[User]


@APIobject
class UserWithObject(JsonResponse):
    user: User
    repository: Repository


@APIobject
class ResponseWithNestedObjects(JsonResponse):
    that_list: list[UserWithObject]


@APIobject
class MetricResponseClass(MetricResponse):
    metric_one: float
    metric_two: dict = APImetric(["label_name"])
    metric_three: int
    metric_four: dict = APImetric(["label_name", "other_label_name"])
    metric_four: dict = APImetric(["label_name", "other_label_name"])
