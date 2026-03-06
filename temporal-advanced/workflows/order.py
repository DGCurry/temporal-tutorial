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

def updated_items_helper(items: Dict[str, int], stock_unit_identifier: str, quantity: int) -> Dict[str, int]:
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
    # Queries are fast and deterministic

    # You create a query by
    # @workflow.query
    # def query_name(self, args) -> return_type:
    #     # implementation here

    # TODO 1
    # add a query get_state that returns the current OrderState dataclass instance

    # --- Signal: single side effect, no return ---
    # Signals are fire-and-forget, and can be used to unblock wait conditions
    # You create a signal by
    # @workflow.signal
    # async def signal_name(self, args) -> None:
    #     # implementation here
    
    # TODO 2
    # add a signal approve that sets state.approved to True

    # --- Update: single side effect, returns new value ---
    # Updates are like signals but return a value. They can be used to change workflow state
    # You create an update by
    # @workflow.update
    # async def update_name(self, args) -> return_type:
    #     # implementation here

    # TODO 3
    # add an update set_email that updates the email in the state and returns the new email


    # --- Orchestration steps: each does one thing ---

    
    async def _wait_for_approval(self) -> None:
        await workflow.wait_condition(lambda: self.state.approved)

    async def _charge_customer(self) -> str:
        # Fill this in: execute the payment child workflow and return the payment receipt. Hint: use workflow.execute_child_workflow.
        # The workflow needs 
        # - the order_id and total price as input arguments,
        # - a deterministic id (hint: use make_payment_workflow_id) and
        # - a parent close policy that terminates the child if the parent is closed.
        #   + See PAYMENT_CHILD_CLOSE_POLICY constant
        return await workflow.execute_child_workflow(
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
