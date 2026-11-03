from datetime import timedelta
from temporalio import workflow
from dataclasses import field
from typing import Any
from dataclasses import dataclass


# Importing activities
with workflow.unsafe.imports_passed_through():
    from src.temporal.activities.ingestion import (
        parse_document_activity,
        chunk_document_activity,
        index_document_activity
    )

INDEX_BATCH_SIZE=100

@dataclass
class FileIngestInput:
    filename: str
    local_path: str


@dataclass
class BatchIngestProgress:
    """
    Progress object associated with the BatchIngestionWorkflow.
    Stores how much has been done and completed.
    """
    status: str="RUNNING"
    files_total: int=0
    files_completed: int=0
    current_filename: str | None=None
    file_results: list[dict[str, Any]]=field(default_factory=list)


@workflow.defn(name="batch-ingestion-workflow")
class BatchIngestionWorkflow:
    """
    This workflow is responsible for orchestrating the batch ingestion of files.
    It parses the documents, chunks them into smaller pieces, and then indexes
    those chunks in batches
    """

    def __init__(self)->None:
        self.progress=BatchIngestProgress()


    # This method defines what happens when an external query comes in
    @workflow.query
    def get_progress(self)->BatchIngestProgress:
        """Returns the current progress of workflow"""
        return self.progress


    @workflow.run
    async def run(self, files: list[FileIngestInput])->BatchIngestProgress:
        """Runs the batch ingestion workflow"""

        batch_size=INDEX_BATCH_SIZE
        self.progress.files_total=len(files)
        self.progress.status="RUNNING"

        for file_input in files:

            # Marking the current file as the file being processed
            self.progress.current_filename=file_input.filename

            # running activity 1: parsing the documents
            document_dictionary=await workflow.execute_activity(
                parse_document_activity,
                args=[file_input.local_path, file_input.filename],
                start_to_close_timeout=timedelta(minutes=30) # if activity isnt completed in 30 min, it will be terminated
            )

            # running activity 2: chunking the parsed documents
            chunk_dictionary=await workflow.execute_activity(
                chunk_document_activity,
                args=[document_dictionary],
                start_to_close_timeout=timedelta(minutes=30)
            )

            indexed=0
            # instead of indexing all chunks in one go, we process them in batches
            for start in range(0, len(chunk_dictionary), batch_size):
                # getting batch of chunks
                batch=chunk_dictionary[start:start+batch_size]

                # running activity 3: indexing the current batch of chunks
                count=await workflow.execute_activity(
                    index_document_activity,
                    args=[batch],
                    start_to_close_timeout=timedelta(minutes=30),
                    heartbeat_timeout=timedelta(minutes=5) # If activity doesnt heartbeat for 5 minutes, it will be terminated
                )
                indexed+=count

            # updating the progress after each file has been indexed
            self.progress.files_completed+=1
            self.progress.file_results.append({
                "filename": file_input.filename,
                "total_chunks_indexed": indexed,
                "document_ids": [],
            })

        self.progress.status="COMPLETED"
        self.progress.current_filename=None
        return self.progress

