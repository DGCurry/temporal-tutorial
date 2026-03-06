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

    wf_id = str(uuid4())

    # TODO start the workflow with client.start_workflow
    # passing in the workflow class, 
    # and specifying the task queue and a unique workflow id. 
    # Store the returned handle in a variable called handle.

    logging.info("Workflow started with id: %s", handle.id)

    result = await handle.result()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
