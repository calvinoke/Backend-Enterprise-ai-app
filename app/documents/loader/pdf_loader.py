from pypdf import PdfReader


class PDFLoader:
    """Extract text from PDF documents."""

    @staticmethod
    def load(path: str) -> str:
        reader = PdfReader(path)
        text_parts: list[str] = []

        for page in reader.pages:
            content = page.extract_text()

            if content:
                text_parts.append(content)

        return "\n".join(text_parts)