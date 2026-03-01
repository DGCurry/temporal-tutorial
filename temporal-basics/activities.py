import logging
from temporalio import activity

logger = logging.getLogger(__name__)

@activity.defn
async def empty_activity() -> None:
    activity.logger.info("empty_activity aangeroepen")
    return None
