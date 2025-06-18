from dataclasses import dataclass
from typing import Any, List, Union

from src.objects.request import RequestData, api_field


@dataclass
class OpenChannelBody(RequestData):
    amount: str = api_field()
    peer_address: str = api_field("peerAddress")


@dataclass
class FundChannelBody(RequestData):
    amount: str = api_field()


@dataclass
class GetChannelsBody(RequestData):
    full_topology: bool = api_field("fullTopology", False)
    including_closed: bool = api_field("includingClosed", False)


@dataclass
class GetPeersBody(RequestData):
    quality: float = api_field()


@dataclass
class CreateSessionBody(RequestData):
    capabilities: List[Any] = api_field()
    destination: str = api_field()
    listen_host: str = api_field("listenHost")
    forward_path: Union[str, dict] = api_field("forwardPath")
    return_path: Union[str, dict] = api_field("returnPath")
    response_buffer: str = api_field("responseBuffer")
    target: Union[str, dict] = api_field()


@dataclass
class SessionCapabilitiesBody(RequestData):
    retransmission: bool = api_field("Retransmission", "false")
    segmentation: bool = api_field("Segmentation", "false")
    no_delay: bool = api_field("NoDelay", "false")


@dataclass
class SessionPathBodyRelayers(RequestData):
    relayers: List[str] = api_field("IntermediatePath")


@dataclass
class SessionTargetBody(RequestData):
    service: int = api_field("Service")
