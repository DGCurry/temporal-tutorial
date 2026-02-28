import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import HelloWorkflow
from overview.activities import empty_activity

TASK_QUEUE = "tutorial-task-queue"
TEMPORAL_ADDRESS = "localhost:7233"  # Standaard voor lokale Temporal-dev

logging.basicConfig(level=logging.INFO)

async def main() -> None:
    # Verbind met de Temporal server
    client = await Client.connect(TEMPORAL_ADDRESS)

    # Start een worker die deze workflow en activity aanbiedt
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[HelloWorkflow],
        activities=[empty_activity],
    )

    logging.info("Worker gestart; luistert op task queue: %s", TASK_QUEUE)
    await worker.run()  # Blokkeert tot je het proces stopt (Ctrl+C)

if __name__ == "__main__":
    asyncio.run(main())
