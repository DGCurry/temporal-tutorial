# worker.py
import logging
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from workflows import OrderWorkflow, PaymentWorkflow
from activities import charge_customer, send_confirmation_email

TASK_QUEUE = "advanced-task-queue"
ADDRESS = "localhost:7233"

logging.basicConfig(level=logging.INFO)

async def main():
    client = await Client.connect(ADDRESS)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[OrderWorkflow, PaymentWorkflow],
        activities=[charge_customer, send_confirmation_email],
    )
    logging.info("Worker up on %s", TASK_QUEUE)
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
