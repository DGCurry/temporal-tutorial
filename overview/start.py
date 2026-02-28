import asyncio
import logging
from uuid import uuid4
from temporalio.client import Client
from workflows import HelloWorkflow

TASK_QUEUE = "tutorial-task-queue"
TEMPORAL_ADDRESS = "localhost:7233"

logging.basicConfig(level=logging.INFO)

async def main() -> None:
    client = await Client.connect(TEMPORAL_ADDRESS)

    # Unieke workflow-id (mag je ook hardcoderen voor idempotentie)
    wf_id = f"hello-{uuid4()}"

    handle = await client.start_workflow(
        HelloWorkflow.run,          # entrypoint van je workflow
        "Diederik",                 # argument voor HelloWorkflow.run
        id=wf_id,
        task_queue=TASK_QUEUE,
    )

    logging.info("Workflow gestart met id: %s", handle.id)

    # Wacht op het resultaat
    result = await handle.result()
    print("Workflow-resultaat:", result)

if __name__ == "__main__":
    asyncio.run(main())
