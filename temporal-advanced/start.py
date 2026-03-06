# start.py
import asyncio
import time
from datetime import timedelta
from temporalio.client import Client
from workflows.order import OrderWorkflow

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
# Connection settings
TASK_QUEUE = "advanced-task-queue"
TEMPORAL_ADDRESS = "localhost:7233"
WORKFLOW_EXECUTION_TIMEOUT = timedelta(minutes=10)

# Client/order details
CLIENT_EMAIL = "hot.man@essent.com"
CLIENT_ORDER_ID = f"ORDER-1001-{int(time.time())}"

# Item details
ITEM_SKU_A = "SKU-AAA"
ITEM_SKU_A_QTY = 2
ITEM_SKU_B = "SKU-BBB"
ITEM_SKU_B_QTY = 1

# Updated email for the update call
UPDATED_EMAIL = "ops@example.com"


async def main():
    client = await Client.connect(TEMPORAL_ADDRESS)

    # Start a workflow
    handle = await client.start_workflow(
        OrderWorkflow.run,
        args=[CLIENT_ORDER_ID, CLIENT_EMAIL],
        id=CLIENT_ORDER_ID,
        task_queue=TASK_QUEUE,
        execution_timeout=WORKFLOW_EXECUTION_TIMEOUT,
    )
    print("Started workflow:", handle.id)

    # Update: set items
    await handle.execute_update(OrderWorkflow.set_item_qty, args=[ITEM_SKU_A, ITEM_SKU_A_QTY])
    await handle.execute_update(OrderWorkflow.set_item_qty, args=[ITEM_SKU_B, ITEM_SKU_B_QTY])

    # Query current state
    state = await handle.query(OrderWorkflow.get_state)
    print("State pre-approval:", state)

    # Signal: approve order (unblocks wait_condition)
    await handle.signal(OrderWorkflow.approve)

    # Optionally update email (returns new value)
    new_email = await handle.execute_update(OrderWorkflow.set_email, UPDATED_EMAIL)
    print("Updated email to:", new_email)

    # Wait for final result
    result = await handle.result()
    print("Workflow result:", result)

if __name__ == "__main__":
    asyncio.run(main())
