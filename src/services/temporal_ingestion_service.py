from dataclasses import asdict
from src.temporal.workflows.ingestion import BatchIngestionWorkflow
from src.configs.temporal_client import get_temporal_client
from src.temporal.workflows.ingestion import FileIngestInput
from src.utils.logger import get_logger
from src.services.ingestion_service import IngestionService
from configs.settings import get_settings

logger=get_logger(__name__)

class TemporalIngestionService:
    """Service for Ingesting documents into vector store using temporal."""

    def __init__(self):
        self.settings=get_settings()
        self.ingestion_service=IngestionService()
    
    async def start_batch_ingestion(self, file_pairs: list[tuple[str, bytes]])->dict:
        """Starts the batch ingestion workflow."""

        # Saving uploaded files to local storage first
        batch_id, paths=self.ingestion_service.save_upload_batch(file_pairs=file_pairs)

        # Preparing the files list for workflow
        files=[
            FileIngestInput(filename=path.name, local_path=str(path)) for path in paths
        ]

        # Start the temporal workflow
        client=await get_temporal_client()
        handle=await client.start_workflow(
            workflow=BatchIngestionWorkflow,
            args=[files],
            id=f"batch-ingestion-{batch_id}",
            task_queue=self.settings.temporal_task_queue
        )

        logger.info(f"Batch ingestion workflow started with ID: {handle.id}")

        return {
            "message": "Batch ingestion workflow started",
            "workflow_id": handle.id,
            "batch_id": batch_id,
            "files_total": len(files),
            "files_name": [file.filename for file in files]
        }
    
    async def get_ingestion_status(self, workflow_id: str)->dict:
        """Get the status of the ingestion workflow."""

        # Get the temporal client
        client=await get_temporal_client()

        # Step 1: Get a handle/reference to a workflow running with this ID
        # (No network call happens here; it's just a local proxy object)
        handle=client.get_workflow_handle(workflow_id=workflow_id)

        progress=None
        try:
            # Step 2: sending a read-only request into a running workflow
            # to extract data or inspect its current internal state from the outside.
            progress=await handle.query(BatchIngestionWorkflow.get_progress)
        except Exception as e:
            progress=None
        
        if progress is not None:
            data=asdict(progress)
            return {
                "workflow_id": workflow_id,
                "status": data.get("status", "UNKNOWN"),
                "files_total": data.get("files_total", 0),
                "files_completed": data.get("files_completed", 0),
                "current_filename": data.get("current_filename"),
                "file_results": data.get("file_results", [])
            }
        
        return {
            "workflow_id": workflow_id,
            "status": "UNKNOWN",
            "files_total": 0,
            "files_completed": 0,
            "current_filename": None,
            "file_results": []
        }