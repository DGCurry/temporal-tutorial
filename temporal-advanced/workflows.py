# workflows.py
import asyncio
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, Optional

from temporalio import workflow
from temporalio.common import RetryPolicy  # <-- juiste import voor RetryPolicy
from temporalio.workflow import ParentClosePolicy  # enum met .TERMINATE / .ABANDON / .REQUEST_CANCEL

from activities import charge_customer, ChargeInput, send_confirmation_email


@dataclass
class OrderState:
    approved: bool = False
    items: Dict[str, int] = field(default_factory=dict)  # sku -> qty
    email: Optional[str] = None
    payment_receipt: Optional[str] = None


@workflow.defn
class PaymentWorkflow:
    """Child workflow: verwerkt betaling via activity met retries."""

    @workflow.run
    async def run(self, order_id: str, amount_eur: float) -> str:
        receipt = await workflow.execute_activity(
            charge_customer,
            ChargeInput(order_id=order_id, amount_eur=amount_eur),
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=5),  # juiste RetryPolicy
        )
        return receipt


@workflow.defn
class OrderWorkflow:
    """
    Parent workflow met:
      - signals (approve)
      - updates (set_item_qty, set_email)
      - queries (get_state, is_approved)
      - wait_condition voor goedkeuring
      - child workflow (PaymentWorkflow)
    """

    # BELANGRIJK: @workflow.init moet op __init__ staan en dezelfde parameters hebben als @workflow.run
    @workflow.init
    def __init__(self, order_id: str, email: str) -> None:
        self.order_id = order_id
        self.state = OrderState(email=email)
        self.total_eur = 0.0

    # ---------- QUERIES (read-only, sync def, geen awaits) ----------
    @workflow.query
    def get_state(self) -> OrderState:
        return self.state

    @workflow.query
    def is_approved(self) -> bool:
        return self.state.approved

    # ---------- SIGNALS (async ok; muteren state) ----------
    @workflow.signal
    async def approve(self) -> None:
        self.state.approved = True

    # ---------- UPDATES (async ok; muteren + return) ----------
    @workflow.update
    async def set_item_qty(self, sku: str, qty: int) -> int:
        if qty < 0:
            # Updates mogen synchronously afwijzen
            raise ValueError("qty must be >= 0")
        self.state.items[sku] = qty
        # simpele prijs: 10 EUR per item
        self.total_eur = sum(q * 10.0 for q in self.state.items.values())
        return self.state.items[sku]

    @workflow.update
    async def set_email(self, address: str) -> str:
        self.state.email = address
        return self.state.email

    # ---------- MAIN ORCHESTRATION ----------
    @workflow.run
    async def run(self, order_id: str, email: str) -> str:
        # 1) Wacht op goedkeuring (her-evalueert alleen bij state changes, b.v. signal/update)
        await workflow.wait_condition(lambda: self.state.approved)

        # 2) Betaal via child workflow
        receipt = await workflow.execute_child_workflow(
            PaymentWorkflow.run,
            self.order_id,
            self.total_eur,
            id=f"{self.order_id}-payment",
            parent_close_policy=ParentClosePolicy.TERMINATE,  # correcte enum-waarde
        )
        self.state.payment_receipt = receipt

        # 3) Bevestigingsmail
        if self.state.email:
            await workflow.execute_activity(
                send_confirmation_email,
                self.order_id,
                self.state.email,
                start_to_close_timeout=timedelta(seconds=5),
            )

        return f"ORDER_OK:{self.order_id}"