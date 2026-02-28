import logging
from temporalio import activity

logger = logging.getLogger(__name__)

@activity.defn
async def empty_activity() -> None:
    """
    Een minimale/lege activity. Doet niets, maar laat zien hoe je activities definieert.
    """
    # Optioneel: log iets, maar returnt verder niets.
    activity.logger.info("empty_activity aangeroepen")
    return None
