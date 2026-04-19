import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReloadModelRequest(_message.Message):
    __slots__ = ("s3_bucket", "s3_prefix")
    S3_BUCKET_FIELD_NUMBER: _ClassVar[int]
    S3_PREFIX_FIELD_NUMBER: _ClassVar[int]
    s3_bucket: str
    s3_prefix: str
    def __init__(self, s3_bucket: _Optional[str] = ..., s3_prefix: _Optional[str] = ...) -> None: ...

class ReloadModelResponse(_message.Message):
    __slots__ = ("success", "message", "new_version")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    NEW_VERSION_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    new_version: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., new_version: _Optional[str] = ...) -> None: ...

class ScoreTransactionRequest(_message.Message):
    __slots__ = ("metadata", "transaction_id", "amount", "currency", "sender_id", "receiver_id", "sender_country", "receiver_country", "device_fingerprint", "channel", "created_at", "transaction_type", "old_balance_orig", "old_balance_dest", "sender_txn_count", "sender_avg_amount", "sender_max_amount", "sender_total_volume", "account_age_hours", "txn_count_1h")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    SENDER_ID_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_ID_FIELD_NUMBER: _ClassVar[int]
    SENDER_COUNTRY_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_COUNTRY_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    OLD_BALANCE_ORIG_FIELD_NUMBER: _ClassVar[int]
    OLD_BALANCE_DEST_FIELD_NUMBER: _ClassVar[int]
    SENDER_TXN_COUNT_FIELD_NUMBER: _ClassVar[int]
    SENDER_AVG_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    SENDER_MAX_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    SENDER_TOTAL_VOLUME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_AGE_HOURS_FIELD_NUMBER: _ClassVar[int]
    TXN_COUNT_1H_FIELD_NUMBER: _ClassVar[int]
    metadata: _common_pb2.RequestMetadata
    transaction_id: str
    amount: float
    currency: str
    sender_id: str
    receiver_id: str
    sender_country: str
    receiver_country: str
    device_fingerprint: str
    channel: str
    created_at: str
    transaction_type: str
    old_balance_orig: float
    old_balance_dest: float
    sender_txn_count: int
    sender_avg_amount: float
    sender_max_amount: float
    sender_total_volume: float
    account_age_hours: float
    txn_count_1h: int
    def __init__(self, metadata: _Optional[_Union[_common_pb2.RequestMetadata, _Mapping]] = ..., transaction_id: _Optional[str] = ..., amount: _Optional[float] = ..., currency: _Optional[str] = ..., sender_id: _Optional[str] = ..., receiver_id: _Optional[str] = ..., sender_country: _Optional[str] = ..., receiver_country: _Optional[str] = ..., device_fingerprint: _Optional[str] = ..., channel: _Optional[str] = ..., created_at: _Optional[str] = ..., transaction_type: _Optional[str] = ..., old_balance_orig: _Optional[float] = ..., old_balance_dest: _Optional[float] = ..., sender_txn_count: _Optional[int] = ..., sender_avg_amount: _Optional[float] = ..., sender_max_amount: _Optional[float] = ..., sender_total_volume: _Optional[float] = ..., account_age_hours: _Optional[float] = ..., txn_count_1h: _Optional[int] = ...) -> None: ...

class ScoreTransactionResponse(_message.Message):
    __slots__ = ("transaction_id", "anomaly_score", "model_version", "fallback_used", "feature_contributions", "decision", "processing_time_ms")
    TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    ANOMALY_SCORE_FIELD_NUMBER: _ClassVar[int]
    MODEL_VERSION_FIELD_NUMBER: _ClassVar[int]
    FALLBACK_USED_FIELD_NUMBER: _ClassVar[int]
    FEATURE_CONTRIBUTIONS_FIELD_NUMBER: _ClassVar[int]
    DECISION_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    transaction_id: str
    anomaly_score: float
    model_version: str
    fallback_used: bool
    feature_contributions: _containers.RepeatedScalarFieldContainer[str]
    decision: str
    processing_time_ms: float
    def __init__(self, transaction_id: _Optional[str] = ..., anomaly_score: _Optional[float] = ..., model_version: _Optional[str] = ..., fallback_used: bool = ..., feature_contributions: _Optional[_Iterable[str]] = ..., decision: _Optional[str] = ..., processing_time_ms: _Optional[float] = ...) -> None: ...
