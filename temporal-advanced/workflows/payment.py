from datetime import timedelta
from entities.charge_input import ChargeInput

from temporalio import workflow
from temporalio.common import RetryPolicy

from activities import charge_customer, ChargeInput

CHARGE_ACTIVITY_TIMEOUT = timedelta(seconds=10)
CHARGE_ACTIVITY_MAX_ATTEMPTS = 5

@workflow.defn
class PaymentWorkflow:
    """Charges the customer. Input → output, delegates side effect to activity."""

    @workflow.run
    async def run(self, order_id: str, amount_euro: float) -> str:
        return await workflow.execute_activity(
            charge_customer,
            ChargeInput(order_id=order_id, amount_euro=amount_euro),
            start_to_close_timeout=CHARGE_ACTIVITY_TIMEOUT,
            retry_policy=RetryPolicy(maximum_attempts=CHARGE_ACTIVITY_MAX_ATTEMPTS),
        )

