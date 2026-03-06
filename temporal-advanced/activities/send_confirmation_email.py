import asyncio

from temporalio import activity

EMAIL_SEND_SLEEP_SECONDS = 0.2

@activity.defn
async def send_confirmation_email(order_id: str, address: str) -> None:
    """Effect: pretend send; idempotent by order_id."""
    _ = (order_id, address)
    await asyncio.sleep(EMAIL_SEND_SLEEP_SECONDS)