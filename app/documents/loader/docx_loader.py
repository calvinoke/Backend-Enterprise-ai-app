from docx import Document


class DOCXLoader:


    @staticmethod
    def load(
        path: str
    ) -> str:


        document = Document(path)

        text = []


        for paragraph in document.paragraphs:

            if paragraph.text:

                text.append(
                    paragraph.text
                )


        return "\n".join(text)