from dataclasses import dataclass, field

from src.objects import JsonResponse


@dataclass(init=False)
class Addresses(JsonResponse):
    native: str = field()


@dataclass(init=False)
class Infos(JsonResponse):
    hopr_node_safe: str = field(metadata={"path": "hoprNodeSafe"})


@dataclass(init=False)
class ConnectedPeer(JsonResponse):
    address: str = field()
    multiaddr: str = field()
    version: str = field(metadata={"path": "reportedVersion"})
