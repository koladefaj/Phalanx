"""Mapper to convert internal Risk Engine state to ML Protobuf messages."""

from aegis_shared.generated.ml_service_pb2 import ScoreTransactionRequest


class MLClientMapper:
    """Maps enriched transaction context to the ML prediction request."""

    @classmethod
    def to_score_proto(cls, enriched_data: dict) -> ScoreTransactionRequest:
        """
        Build ScoreTransactionRequest proto.
        This must include ALL fields required by the ML _assemble_features logic.
        """
        return ScoreTransactionRequest(
            transaction_id=str(enriched_data.get("transaction_id", "")),
            amount=float(enriched_data.get("amount", 0.0)),
            transaction_type=str(enriched_data.get("transaction_type", "TRANSFER")),
            channel=str(enriched_data.get("channel", "web")),
            
            # Geographic
            sender_country=str(enriched_data.get("sender_country", "")),
            receiver_country=str(enriched_data.get("receiver_country", "")),
            
            # Balances
            old_balance_orig=float(enriched_data.get("old_balance_orig", 0.0)),
            old_balance_dest=float(enriched_data.get("old_balance_dest", 0.0)),
            
            # Redis Enriched Stats
            sender_txn_count=int(enriched_data.get("sender_txn_count", 0)),
            sender_avg_amount=float(enriched_data.get("sender_avg_amount", 0.0)),
            sender_max_amount=float(enriched_data.get("sender_max_amount", 0.0)),
            sender_total_volume=float(enriched_data.get("sender_total_volume", 0.0)),
            account_age_hours=float(enriched_data.get("account_age_hours", 24.0)),
            txn_count_1h=int(enriched_data.get("txn_count_1h", 0)),
        )