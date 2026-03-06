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

        # TODO 1
        # Now, we must run the greeting activity

        # TODO 2
        # Now, we must return the greeting
