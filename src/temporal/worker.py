import asyncio
from src.temporal.workflows.ingestion import BatchIngestionWorkflow
from src.configs.temporal_client import get_temporal_client
from src.configs.settings import get_settings
from src.utils.logger import get_logger
from temporalio.worker import Worker

from src.temporal.activities.ingestion import (
    parse_document_activity,
    chunk_document_activity,
    index_document_activity,
    ingest_file_activity
)

logger=get_logger(__name__)

async def main()->None:
    settings=get_settings()

    client=await get_temporal_client()

    # Creating worker instance
    worker=Worker(
        client=client,
        task_queue=settings.temporal_task_queue, # Which task queue will this worker poll on
        workflows=[BatchIngestionWorkflow], # What all workflows the worker has to keep an eye on
        activities=[ # What all activities the worker can run
            parse_document_activity,
            chunk_document_activity,
            index_document_activity,
            ingest_file_activity
        ]
    )

    logger.info(f"Temporal worker started for queue: {settings.temporal_task_queue}")
    await worker.run()


if __name__=="__main__":
    asyncio.run(main())