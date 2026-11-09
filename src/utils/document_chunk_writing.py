from langchain_core.documents import Document
from pathlib import Path
import json

def staging_directory_upload(upload_path: Path)->Path:
    """Creating staging directory inside the upload path"""

    directory=upload_path.parent / "staging"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def spill_path_for_upload(upload_path: Path, filename: str, stage: str)->Path:
    """Gets the spill path for the upload file
    
    Args:
        upload_path: The path to the upload file
        filename: The name of the file
        stage: The stage of the file
    Returns:
        The path to the spill file
    """

    # Getting the stem of file without its extension
    filestem=Path(upload_path).stem
    return staging_directory_upload(upload_path=upload_path) / f"{filestem}.{stage}.jsonl"


def write_documents_to_jsonl(path: Path, documents: list[Document])->int:
    """Writes the document to JSONL format inside disk/path
    
    Args:
        path: The path to write the document to
        documents: The list of documents to write to the file
    Returns:
        The number of documents written to the file
    """

    path.parent.mkdir(parents=True, exist_ok=True)

    count=0
    with path.open("w", encoding="utf-8") as f:
        for doc in documents:
            record={"file_content": doc.page_content, "metadata": doc.metadata}
            f.write(json.dumps(record, ensure_ascii=False)+"\n")
            count+=1
    
    return count


def read_documents_from_jsonl_batch(path: Path, offset: int, limit: int)->list[Document]:
    """Reads a batch of documents from a JSONL file
    
    Args:
        path: The path to the JSONL file
        offset: Beginning lines to skip
        limit: Maximum number of documents to read
    Returns:
        The list of documents read from the file
    """
    
    documents=[]

    if limit<=0:
        limit=10
    
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f):
            text=line.strip()
            if not text:
                continue

            # Skipping the lines before the offset value
            if line_number<offset:
                continue

            # Breaking the loop if the number of documents reaches the limit
            if len(documents)>=limit:
                break

            payload=json.loads(text)
            documents.append(Document(page_content=payload["page_content"], metadata=payload["metadata"]))
    
    return documents


def count_jsonl_lines(path: Path)->int:
    with path.open("r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())