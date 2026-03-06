import asyncio
import logging
from uuid import uuid4
from temporalio.client import Client

TASK_QUEUE = "tutorial-task-queue"
TEMPORAL_ADDRESS = "localhost:7233"

logging.basicConfig(level=logging.INFO)

async def main() -> None:
    client = await Client.connect(TEMPORAL_ADDRESS)

    wf_id = str(uuid4())

    handle = await client.start_workflow(
        "HelloWorkflow",
        id=wf_id,
        task_queue=TASK_QUEUE
    )

    logging.info("Workflow started with id: %s", handle.id)

    result = await handle.result()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
