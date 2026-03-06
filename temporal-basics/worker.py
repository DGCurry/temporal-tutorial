import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import HelloWorkflow
from activities import greeting_activity
from start import TASK_QUEUE

TEMPORAL_ADDRESS = "localhost:7233"

logging.basicConfig(level=logging.INFO)

async def main() -> None:
    client = await Client.connect(TEMPORAL_ADDRESS)

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[HelloWorkflow],
        activities=[greeting_activity],
    )

    logging.info("Worker gestart; luistert op task queue: %s", TASK_QUEUE)
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
