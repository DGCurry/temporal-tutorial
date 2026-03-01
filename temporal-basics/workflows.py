import logging
from datetime import timedelta
from temporalio import workflow
from activities import empty_activity

logger = logging.getLogger(__name__)

@workflow.defn
class HelloWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        workflow.logger.info("Workflow started")

        await workflow.execute_activity(
            empty_activity,
            start_to_close_timeout=timedelta(seconds=5),
        )

        return f"Hello, {name}! 👋"
