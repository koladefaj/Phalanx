import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InvestigateRequest(_message.Message):
    __slots__ = ("metadata", "transaction_id", "sender_id")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    SENDER_ID_FIELD_NUMBER: _ClassVar[int]
    metadata: _common_pb2.RequestMetadata
    transaction_id: str
    sender_id: str
    def __init__(self, metadata: _Optional[_Union[_common_pb2.RequestMetadata, _Mapping]] = ..., transaction_id: _Optional[str] = ..., sender_id: _Optional[str] = ...) -> None: ...

class InvestigateResponse(_message.Message):
    __slots__ = ("transaction_id", "verdict", "confidence", "summary", "recommendation", "agent_name")
    TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    VERDICT_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDATION_FIELD_NUMBER: _ClassVar[int]
    AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    transaction_id: str
    verdict: str
    confidence: str
    summary: str
    recommendation: str
    agent_name: str
    def __init__(self, transaction_id: _Optional[str] = ..., verdict: _Optional[str] = ..., confidence: _Optional[str] = ..., summary: _Optional[str] = ..., recommendation: _Optional[str] = ..., agent_name: _Optional[str] = ...) -> None: ...
