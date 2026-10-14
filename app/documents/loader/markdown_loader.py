
class MarkdownLoader:
    """Load Markdown documents as plain text for RAG processing."""

    @staticmethod
    def load(path: str) -> str:
        with open(
            path,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as file:
            return file.read()