import logging
from temporalio import activity

logger = logging.getLogger(__name__)

@activity.defn
async def greeting_activity() -> None:
    activity.logger.info("greetings, my padawan")
    return "padawan"