import logging
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from app.embeddings.service import EmbeddingService
from app.rag.repository import DocumentChunkRepository
from app.documents.loader.factory import LoaderFactory

from .chunker import DocumentChunker
from .models import (
    Document,
    DocumentStatus,
    DocumentType,
)
from .repository import DocumentRepository


logger = logging.getLogger(__name__)


UPLOAD_DIRECTORY = Path(
    "storage/documents"
)

UPLOAD_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


ALLOWED_EXTENSIONS = {
    "pdf": DocumentType.PDF,
    "docx": DocumentType.DOCX,
    "txt": DocumentType.TXT,
    "md": DocumentType.MD,
}


class DocumentService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.repo = DocumentRepository(
            db
        )

        self.chunker = DocumentChunker()

        self.embedding_service = (
            EmbeddingService()
        )

        self.chunk_repository = (
            DocumentChunkRepository(db)
        )

    # =====================================================
    # UPLOAD
    # =====================================================

    async def upload_document(
        self,
        filename: str,
        file_bytes: bytes,
        uploaded_by: UUID,
    ) -> Document:

        if not filename:
            raise ValueError(
                "Filename is required."
            )

        extension = (
            Path(filename)
            .suffix
            .lower()
            .lstrip(".")
        )

        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(
                "Unsupported document type. "
                f"Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        if not file_bytes:
            raise ValueError(
                "Uploaded file is empty."
            )

        stored_name = (
            f"{uuid4()}.{extension}"
        )

        path = (
            UPLOAD_DIRECTORY
            / stored_name
        )

        path.write_bytes(
            file_bytes
        )

        document = Document(
            filename=stored_name,
            original_filename=filename,
            document_type=(
                ALLOWED_EXTENSIONS[
                    extension
                ]
            ),
            status=DocumentStatus.PENDING,
            uploaded_by=uploaded_by,
        )

        return await self.repo.create(
            document
        )

    # =====================================================
    # LIST
    # =====================================================

    async def list_documents(
        self,
        user_id: UUID,
    ):

        return await self.repo.list(
            user_id=user_id
        )

    # =====================================================
    # GET
    # =====================================================

    async def get_document(
        self,
        document_id: UUID,
        user_id: UUID,
    ):

        return await self.repo.get(
            document_id=document_id,
            user_id=user_id,
        )

    # =====================================================
    # DELETE
    # =====================================================

    async def delete_document(
        self,
        document_id: UUID,
        user_id: UUID,
    ):

        document = await self.repo.get(
            document_id=document_id,
            user_id=user_id,
        )

        if not document:
            raise ValueError(
                "Document not found."
            )

        path = (
            UPLOAD_DIRECTORY
            / document.filename
        )

        if path.exists():
            path.unlink()

        await self.repo.delete(
            document
        )

    # =====================================================
    # PROCESS DOCUMENT
    # =====================================================

    async def process_document(
        self,
        document_id: UUID,
        user_id: UUID,
    ):

        document = await self.repo.get(
            document_id=document_id,
            user_id=user_id,
        )

        if not document:
            raise ValueError(
                "Document not found."
            )

        try:

            # -----------------------------------------
            # 1. PROCESSING
            # -----------------------------------------

            document.status = (
                DocumentStatus.PROCESSING
            )

            await self.repo.update(
                document
            )

            # -----------------------------------------
            # 2. FIND FILE
            # -----------------------------------------

            path = (
                UPLOAD_DIRECTORY
                / document.filename
            )

            if not path.exists():
                raise FileNotFoundError(
                    "Stored document file is missing."
                )

            # -----------------------------------------
            # 3. LOAD DOCUMENT
            # -----------------------------------------

            loader = LoaderFactory.get_loader(
                document.document_type
            )

            if not loader:
                raise ValueError(
                    "No loader available for "
                    f"{document.document_type}."
                )

            text = loader.load(
                str(path)
            )

            if not text or not text.strip():
                raise ValueError(
                    "No text could be extracted "
                    "from the document."
                )

            # -----------------------------------------
            # 4. SAVE FULL TEXT
            # -----------------------------------------

            document.content = text

            await self.repo.update(
                document
            )

            # -----------------------------------------
            # 5. REMOVE OLD CHUNKS
            # -----------------------------------------

            await self.chunk_repository.delete_by_document(
                str(document.id)
            )

            # -----------------------------------------
            # 6. CHUNK DOCUMENT
            # -----------------------------------------

            chunks = self.chunker.split(
                text
            )

            if not chunks:
                raise ValueError(
                    "Document produced no chunks."
                )

            logger.info(
                "Document %s split into %s chunks.",
                document.id,
                len(chunks),
            )

            # -----------------------------------------
            # 7. GENERATE EMBEDDINGS
            # -----------------------------------------

            embeddings = (
                await self.embedding_service.generate_embeddings(
                    chunks
                )
            )

            if len(embeddings) != len(chunks):
                raise ValueError(
                    "Number of embeddings does not "
                    "match number of chunks."
                )

            # -----------------------------------------
            # 8. STORE CHUNKS + EMBEDDINGS
            # -----------------------------------------

            await self.chunk_repository.create_many(
                document_id=str(document.id),
                chunks=chunks,
                embeddings=embeddings,
            )

            # -----------------------------------------
            # 9. READY
            # -----------------------------------------

            document.status = (
                DocumentStatus.READY
            )

            await self.repo.update(
                document
            )

            logger.info(
                "Document %s processed successfully. "
                "Chunks=%s",
                document.id,
                len(chunks),
            )

            return document

        except Exception:

            logger.exception(
                "Document processing failed: %s",
                document.id,
            )

            document.status = (
                DocumentStatus.FAILED
            )

            await self.repo.update(
                document
            )

            raise