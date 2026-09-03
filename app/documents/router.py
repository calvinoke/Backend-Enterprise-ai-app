from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from app.core.logging import get_logger
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
    service: DocumentService = Depends(
        get_document_service
    ),
):
    """
    Upload a document to the document storage system.

    The document is stored on disk and a database record
    is created with PENDING status.
    """

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
        )

        content = await file.read()

        if not content:

            logger.warning(
                "Document upload rejected: empty file",
                filename=file.filename,
            )

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        document = await service.upload_document(
            filename=file.filename,
            file_bytes=content,
            uploaded_by="admin",
        )

        logger.info(
            "Document uploaded successfully",
            document_id=str(document.id),
            filename=file.filename,
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
    service: DocumentService = Depends(
        get_document_service
    ),
):
    """
    Return all documents.
    """

    try:

        logger.info(
            "Listing documents"
        )

        documents = await service.list_documents()

        logger.info(
            "Documents retrieved successfully",
            count=len(documents),
        )

        return documents

    except Exception as exc:

        logger.exception(
            "Failed to list documents",
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
    service: DocumentService = Depends(
        get_document_service
    ),
):
    """
    Retrieve a single document by ID.
    """

    try:

        logger.info(
            "Retrieving document",
            document_id=str(document_id),
        )

        document = await service.get_document(
            document_id
        )

        if not document:

            logger.warning(
                "Document not found",
                document_id=str(document_id),
            )

            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        logger.info(
            "Document retrieved successfully",
            document_id=str(document_id),
        )

        return document

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Failed to retrieve document",
            document_id=str(document_id),
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
    "/{document_id}",)
async def delete_document(
    document_id: UUID,
    service: DocumentService = Depends(
        get_document_service
    ),
):
    """
    Delete a document from storage and the database.
    """

    try:

        logger.info(
            "Deleting document",
            document_id=str(document_id),
        )

        await service.delete_document(
            document_id
        )

        logger.info(
            "Document deleted successfully",
            document_id=str(document_id),
        )

        return {
            "message": "Document deleted successfully."
        }

    except ValueError as exc:

        logger.warning(
            "Document deletion failed",
            document_id=str(document_id),
            error=str(exc),
        )

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        logger.exception(
            "Unexpected error deleting document",
            document_id=str(document_id),
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
    service: DocumentService = Depends(
        get_document_service
    ),
):
    """
    Process a document.

    The processing pipeline extracts text from the uploaded
    file and stores the extracted content in the database.
    """

    try:

        logger.info(
            "Starting document processing",
            document_id=str(document_id),
        )

        document = await service.process_document(
            document_id
        )

        logger.info(
            "Document processed successfully",
            document_id=str(document_id),
            status=(
                document.status.value
                if document.status
                else None
            ),
        )

        return document

    except ValueError as exc:

        logger.warning(
            "Document processing validation failed",
            document_id=str(document_id),
            error=str(exc),
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except FileNotFoundError as exc:

        logger.error(
            "Document file not found during processing",
            document_id=str(document_id),
            error=str(exc),
        )

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        logger.exception(
            "Unexpected error processing document",
            document_id=str(document_id),
            error=str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process document.",
        ) from exc