import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from temporalio import activity
from temporalio.exceptions import ApplicationError


@dataclass
class ChargeInput:
    order_id: str
    amount_eur: float
    idempotency_key: Optional[str] = None


@activity.defn
async def charge_customer(inp: ChargeInput) -> str:
    """
    Simulates an external payment call.
    Demonstrates:
      - ApplicationError (retryable/non-retryable)
      - Heartbeating
      - Cooperative cancellation
    """
    info = activity.info()
    # Strong idempotency key for external APIs (retries may re-call this)
    idem_key = inp.idempotency_key or f"{info.workflow_run_id}-{info.activity_id}"

    # Long-running work with heartbeat and cancellation handling
    try:
        for step in range(5):
            await asyncio.sleep(0.5)
            activity.heartbeat({"step": step, "order_id": inp.order_id})
        # Simulate a transient failure on first few attempts:
        if info.attempt < 3:
            raise ApplicationError(
                "Payment gateway timeout",
                type="GatewayTimeout",
                # retryable by default; leave non_retryable=False
            )
        return f"CHARGE_OK:{idem_key}"
    except asyncio.CancelledError:
        # Cleanup if needed (e.g., reverse auth) and then re-raise
        raise


@activity.defn
async def send_confirmation_email(order_id: str, address: str) -> None:
    # pretend send; idempotent by order_id
    await asyncio.sleep(0.2)
