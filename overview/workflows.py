import logging
from datetime import timedelta
from temporalio import workflow
from overview.activities import empty_activity  # referentie naar jouw activity-functie

logger = logging.getLogger(__name__)

@workflow.defn
class HelloWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        """
        Simpele workflow:
        - Roept een lege activity aan (met vereiste timeout)
        - Retourneert een vriendelijk bericht
        """
        workflow.logger.info("Workflow gestart", extra={"name": name})

        # Belangrijk: voor activiteiten MOET je een timeout opgeven
        await workflow.execute_activity(
            empty_activity,
            start_to_close_timeout=timedelta(seconds=5),
        )

        return f"Hallo, {name}! 👋"
