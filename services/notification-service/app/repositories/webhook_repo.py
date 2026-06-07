import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook import Webhook


class WebhookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, client_id: str, url: str, events: List[str]) -> Webhook:
        webhook = Webhook(
            webhook_id=uuid.uuid4(),
            client_id=client_id,
            url=url,
            events=events,
        )
        self.session.add(webhook)
        await self.session.flush()
        return webhook

    async def get_by_id(self, webhook_id: uuid.UUID) -> Optional[Webhook]:
        result = await self.session.execute(
            select(Webhook).where(Webhook.webhook_id == webhook_id)
        )
        return result.scalar_one_or_none()

    async def get_active_for_client_and_event(
        self, client_id: str, event: str
    ) -> List[Webhook]:
        result = await self.session.execute(
            select(Webhook).where(
                Webhook.client_id == client_id,
                Webhook.is_active == True,  # noqa: E712
                Webhook.events.any(event),
            )
        )
        return list(result.scalars().all())

    async def increment_delivery(self, webhook_id: uuid.UUID, success: bool) -> None:
        if success:
            await self.session.execute(
                update(Webhook)
                .where(Webhook.webhook_id == webhook_id)
                .values(
                    delivery_count=Webhook.delivery_count + 1,
                    last_delivery_at=datetime.now(timezone.utc),
                )
            )
        else:
            await self.session.execute(
                update(Webhook)
                .where(Webhook.webhook_id == webhook_id)
                .values(failure_count=Webhook.failure_count + 1)
            )
