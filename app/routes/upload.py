from fastapi import APIRouter, Depends, UploadFile, File, Query
from ..services.file_processing import process_uploaded_file
from ..core.security import get_current_user

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/process")
async def upload_and_process(
    file: UploadFile = File(...),
    use_ai: bool = Query(False, description="Use AI (OpenAI GPT) for extraction"),
    current_user=Depends(get_current_user)
):
    """
    Upload and process DFC file (PDF, Excel, CSV).
    Returns extracted fields pre-formatted for DFC creation form.
    """
    result = await process_uploaded_file(file, use_ai=use_ai)
    return result
