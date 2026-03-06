
import asyncio
from dataclasses import dataclass
from typing import Optional

from entities.charge_input import ChargeInput

from temporalio import activity
from temporalio.exceptions import ApplicationError

UPPER_BOUND_RETRY = 4
HEARTBEAT_SLEEP_SECONDS = 0.5
MIN_ATTEMPTS_BEFORE_SUCCESS = 3
PAYMENT_ERROR_TYPE = "GatewayTimeout"
PAYMENT_ERROR_MESSAGE = "Payment gateway timeout"
CHARGE_OK_PREFIX = "CHARGE_OK"
CHARGE_NOK_PREFIX = "CHARGE_NOK"

def resolve_idempotency_key(explicit_key: Optional[str], run_id: str, activity_id: str) -> str:
    """Pure: pick the explicit key or derive one from workflow/activity IDs."""
    return explicit_key if explicit_key is not None else f"{run_id}-{activity_id}"


def format_charge_result(prefix: str, idempotency_key: str) -> str:
    """Pure: build the canonical charge-result string."""
    return f"{prefix}:{idempotency_key}"


def should_fail(attempt: int, threshold: int) -> bool:
    """Pure: decide whether the current attempt should fail transiently."""
    return attempt < threshold


def make_transient_error() -> ApplicationError:
    """Pure: construct the transient payment error."""
    return ApplicationError(PAYMENT_ERROR_MESSAGE, type=PAYMENT_ERROR_TYPE)


async def heartbeat_loop(order_id: str, steps: int, interval: float) -> None:
    """Effect: sleep and heartbeat for each step."""
    for step in range(steps + 1):
        await asyncio.sleep(interval)
        activity.heartbeat({"step": step, "order_id": order_id})

@activity.defn
async def charge_customer(inp: ChargeInput) -> str:
    """Simulates an external payment call."""
    info = activity.info()
    idem_key = resolve_idempotency_key(inp.idempotency_key, info.workflow_run_id, info.activity_id)

    try:
        await heartbeat_loop(inp.order_id, UPPER_BOUND_RETRY, HEARTBEAT_SLEEP_SECONDS)

        if should_fail(info.attempt, MIN_ATTEMPTS_BEFORE_SUCCESS):
            raise make_transient_error()

        return format_charge_result(CHARGE_OK_PREFIX, idem_key)

    except asyncio.CancelledError:
        return format_charge_result(CHARGE_NOK_PREFIX, idem_key)


