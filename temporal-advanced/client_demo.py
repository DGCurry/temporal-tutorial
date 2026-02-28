import asyncio
from datetime import timedelta
from temporalio.client import Client
from workflows import OrderWorkflow

TASK_QUEUE = "advanced-task-queue"
ADDRESS = "localhost:7233"

async def main():
    client = await Client.connect(ADDRESS)

    # Start a workflow
    handle = await client.start_workflow(
        OrderWorkflow.run,
        "ORDER-1001",                   # order_id
        "alice@example.com",            # email (initializer)
        id="ORDER-1001",
        task_queue=TASK_QUEUE,
        execution_timeout=timedelta(minutes=10),
    )
    print("Started workflow:", handle.id)

    # Update: set items
    await handle.execute_update(OrderWorkflow.set_item_qty, "SKU-AAA", 2)
    await handle.execute_update(OrderWorkflow.set_item_qty, "SKU-BBB", 1)

    # Query current state
    state = await handle.query(OrderWorkflow.get_state)
    print("State pre-approval:", state)

    # Signal: approve order (unblocks wait_condition)
    await handle.signal(OrderWorkflow.approve)

    # Optionally update email (returns new value)
    new_email = await handle.execute_update(OrderWorkflow.set_email, "ops@example.com")
    print("Updated email to:", new_email)

    # Wait for final result
    result = await handle.result()
    print("Workflow result:", result)

if __name__ == "__main__":
    asyncio.run(main())
