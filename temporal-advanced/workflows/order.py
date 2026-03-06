from datetime import timedelta
from typing import Dict

from entities.order_state import OrderState

from temporalio import workflow
from temporalio.workflow import ParentClosePolicy

from workflows.payment import PaymentWorkflow
from activities import send_confirmation_email


EMAIL_ACTIVITY_TIMEOUT = timedelta(seconds=5)
ORDER_RESULT_PREFIX = "ORDER_OK"
PAYMENT_WORKFLOW_ID_SUFFIX = "-payment"
PRICE_PER_ITEM_EUR = 10.0
PAYMENT_CHILD_CLOSE_POLICY = ParentClosePolicy.TERMINATE

def compute_total_items_price(items: Dict[str, int], price_per_item: float) -> float:
    """Pure: compute total from items dict."""
    return sum(quantity * price_per_item for quantity in items.values())

def make_payment_workflow_id(order_id: str) -> str:
    """Pure: derive the child workflow id."""
    return f"{order_id}{PAYMENT_WORKFLOW_ID_SUFFIX}"


def make_order_result(order_id: str) -> str:
    """Pure: build the final result string."""
    return f"{ORDER_RESULT_PREFIX}:{order_id}"

def updated_items(items: Dict[str, int], stock_unit_identifier: str, quantity: int) -> Dict[str, int]:
    """Pure: return a new items dict with the given sku set to quantity."""
    if quantity < 0:
        raise ValueError("qty must be >= 0")
    return {**items, stock_unit_identifier: quantity}

@workflow.defn
class OrderWorkflow:

    @workflow.init
    def __init__(self, order_id: str, email: str) -> None:
        self.order_id = order_id
        self.state = OrderState(email=email)

    # --- Queries: pure reads, no side effects ---

    @workflow.query
    def get_state(self) -> OrderState:
        return self.state

    @workflow.query
    def is_approved(self) -> bool:
        return self.state.approved

    # --- Signal: single side effect, no return ---

    @workflow.signal
    async def approve(self) -> None:
        self.state.approved = True

    # --- Updates: single mutation + return the new value ---

    @workflow.update
    async def set_item_quantity(self, stock_unit_identifier: str, quantity: int) -> Dict[str, int]:
        """Replaces items with an updated copy. Returns the new items dict."""
        self.state.items = updated_items(self.state.items, stock_unit_identifier, quantity)
        return self.state.items

    @workflow.update
    async def set_email(self, address: str) -> str:
        """Replace the email. Returns the new address."""
        self.state.email = address
        return self.state.email

    # --- Orchestration steps: each does one thing ---

    async def _wait_for_approval(self) -> None:
        """Side effect: blocks until approved."""
        await workflow.wait_condition(lambda: self.state.approved)

    async def _charge_customer(self) -> str:
        """Input → output: runs child workflow, returns receipt."""
        return await workflow.execute_child_workflow(
            PaymentWorkflow.run,
            args=[self.order_id, compute_total_items_price(self.state.items, PRICE_PER_ITEM_EUR)],
            id=make_payment_workflow_id(self.order_id),
            parent_close_policy=PAYMENT_CHILD_CLOSE_POLICY,
        )

    async def _send_email(self, email: str) -> None:
        """Side effect: sends confirmation email, no return."""
        await workflow.execute_activity(
            send_confirmation_email,
            args=[self.order_id, email],
            start_to_close_timeout=EMAIL_ACTIVITY_TIMEOUT,
        )

    # --- Main workflow method: orchestrates the steps ---
    @workflow.run
    async def run(self) -> str:
        await self._wait_for_approval()

        self.state.payment_receipt = await self._charge_customer()

        has_email = self.state.email is not None
        if has_email:
            await self._send_email(self.state.email)

        return make_order_result(self.order_id)