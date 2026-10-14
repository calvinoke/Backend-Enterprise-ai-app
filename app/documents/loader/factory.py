from app.documents.models import DocumentType

from app.documents.loader.pdf_loader import PDFLoader
from app.documents.loader.docx_loader import DOCXLoader
from app.documents.loader.txt_loader import TXTLoader
from app.documents.loader.markdown_loader import MarkdownLoader


class LoaderFactory:
    """Return the appropriate document loader."""

    @staticmethod
    def get_loader(document_type: DocumentType):
        if document_type == DocumentType.PDF:
            return PDFLoader()

        if document_type == DocumentType.DOCX:
            return DOCXLoader()

        if document_type == DocumentType.TXT:
            return TXTLoader()

        if document_type == DocumentType.MD:
            return MarkdownLoader()

        raise ValueError(
            f"Unsupported document type: {document_type}"
        )