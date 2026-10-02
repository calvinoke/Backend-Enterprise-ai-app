from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from app.auth.dependencies import get_current_user
from app.core.logging import get_logger
from app.users.models import User

from .dependencies import (
    get_document_service,
)
from .schemas import (
    DocumentResponse,
    DocumentUploadResponse,
)
from .service import (
    DocumentService,
)


logger = get_logger(__name__)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


# =========================================================
# Upload Document
# =========================================================

@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
)
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    service: DocumentService = Depends(
        get_document_service
    ),
):

    try:

        if not file.filename:
            logger.warning(
                "Document upload rejected: missing filename"
            )

            raise HTTPException(
                status_code=400,
                detail="Filename is required.",
            )

        logger.info(
            "Starting document upload",
            filename=file.filename,
            content_type=file.content_type,
            user_id=str(user.id),
        )

        content = await file.read()

        if not content:
            logger.warning(
                "Document upload rejected: empty file",
                filename=file.filename,
                user_id=str(user.id),
            )

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        document = await service.upload_document(
            filename=file.filename,
            file_bytes=content,
            uploaded_by=user.id,
        )

        logger.info(
            "Document uploaded successfully",
            document_id=str(document.id),
            filename=file.filename,
            user_id=str(user.id),
            document_type=(
                document.document_type.value
                if document.document_type
                else None
            ),
            status=(
                document.status.value
                if document.status
                else None
            ),
        )

        return document

    except HTTPException:
        raise

    except ValueError as exc:

        logger.warning(
            "Document upload validation failed",
            filename=file.filename,
            user_id=str(user.id),
            error=str(exc),
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        logger.exception(
            "Unexpected error during document upload",
            filename=file.filename,
            user_id=str(user.id),
            error=str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to upload document.",
        ) from exc


# =========================================================
# List Documents
# =========================================================

@router.get(
    "/",
    response_model=list[DocumentResponse],
)
async def list_documents(
    user: User = Depends(get_current_user),
    service: DocumentService = Depends(
        get_document_service
    ),
):

    try:

        documents = await service.list_documents(
            user_id=user.id
        )

        logger.info(
            "Documents retrieved successfully",
            user_id=str(user.id),
            count=len(documents),
        )

        return documents

    except Exception as exc:

        logger.exception(
            "Failed to list documents",
            user_id=str(user.id),
            error=str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve documents.",
        ) from exc


# =========================================================
# Get Document
# =========================================================

@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(
    document_id: UUID,
    user: User = Depends(get_current_user),
    service: DocumentService = Depends(
        get_document_service
    ),
):

    try:

        document = await service.get_document(
            document_id=document_id,
            user_id=user.id,
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        return document

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Failed to retrieve document",
            document_id=str(document_id),
            user_id=str(user.id),
            error=str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve document.",
        ) from exc


# =========================================================
# Delete Document
# =========================================================

@router.delete(
    "/{document_id}",
)
async def delete_document(
    document_id: UUID,
    user: User = Depends(get_current_user),
    service: DocumentService = Depends(
        get_document_service
    ),
):

    try:

        await service.delete_document(
            document_id=document_id,
            user_id=user.id,
        )

        logger.info(
            "Document deleted successfully",
            document_id=str(document_id),
            user_id=str(user.id),
        )

        return {
            "message": "Document deleted successfully."
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        logger.exception(
            "Unexpected error deleting document",
            document_id=str(document_id),
            user_id=str(user.id),
            error=str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to delete document.",
        ) from exc


# =========================================================
# Process Document
# =========================================================

@router.post(
    "/{document_id}/process",
    response_model=DocumentResponse,
)
async def process_document(
    document_id: UUID,
    user: User = Depends(get_current_user),
    service: DocumentService = Depends(
        get_document_service
    ),
):

    try:

        logger.info(
            "Starting document processing",
            document_id=str(document_id),
            user_id=str(user.id),
        )

        document = await service.process_document(
            document_id=document_id,
            user_id=user.id,
        )

        logger.info(
            "Document processed successfully",
            document_id=str(document_id),
            user_id=str(user.id),
            status=(
                document.status.value
                if document.status
                else None
            ),
        )

        return document

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        logger.exception(
            "Unexpected error processing document",
            document_id=str(document_id),
            user_id=str(user.id),
            error=str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process document.",
        ) from exc