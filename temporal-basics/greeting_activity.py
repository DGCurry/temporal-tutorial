import logging
from temporalio import activity

logger = logging.getLogger(__name__)

@activity.defn
async def greeting_activity() -> str:
    activity.logger.info("greetings, my padawan")
    return "padawan"