import logging
from datetime import timedelta
from temporalio import workflow
from activities import greeting_activity

logger = logging.getLogger(__name__)

@workflow.defn
class HelloWorkflow:
    @workflow.run
    async def run(self) -> str:
        workflow.logger.info("Workflow started")

        greeting = await workflow.execute_activity(
            greeting_activity,
            start_to_close_timeout=timedelta(seconds=5),
        )

        return f"Hello, {greeting}!"
