class TXTLoader:
    """Read plain-text documents."""

    @staticmethod
    def load(path: str) -> str:
        with open(
            path,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as file:
            return file.read()