from pypdf import PdfReader


class PDFLoader:


    @staticmethod
    def load(
        path: str
    ) -> str:

        reader = PdfReader(path)

        text = ""

        for page in reader.pages:

            content = page.extract_text()

            if content:

                text += content + "\n"


        return text