import hashlib
import hmac
import json
import time
from typing import Any, Dict

import httpx

from aegis_shared.utils.logging import get_logger
from app.config import settings

logger = get_logger("webhook-delivery")


class WebhookDeliveryService:
    """Delivers webhook payloads with HMAC signatures and retry logic."""

    def __init__(self):
        self._secret = settings.WEBHOOK_SECRET.encode()
        self._timeout = settings.WEBHOOK_TIMEOUT_SECONDS
        self._max_retries = settings.WEBHOOK_MAX_RETRIES

    def _sign(self, payload: str) -> str:
        return hmac.new(self._secret, payload.encode(), hashlib.sha256).hexdigest()

    async def deliver(self, url: str, event: str, payload: Dict[str, Any]) -> bool:
        body = json.dumps(payload, default=str)
        signature = self._sign(body)
        headers = {
            "Content-Type": "application/json",
            "X-Aegis-Event": event,
            "X-Aegis-Signature": f"sha256={signature}",
            "X-Aegis-Timestamp": str(int(time.time())),
        }

        for attempt in range(1, self._max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.post(url, content=body, headers=headers)
                    if response.is_success:
                        logger.info(
                            "webhook_delivered",
                            url=url,
                            event=event,
                            status_code=response.status_code,
                            attempt=attempt,
                        )
                        return True
                    logger.warning(
                        "webhook_non_success_response",
                        url=url,
                        status_code=response.status_code,
                        attempt=attempt,
                    )
            except httpx.TimeoutException:
                logger.warning("webhook_timeout", url=url, attempt=attempt)
            except Exception as e:
                logger.warning("webhook_delivery_error", url=url, error=str(e), attempt=attempt)

        logger.error("webhook_delivery_failed_all_retries", url=url, event=event)
        return False
