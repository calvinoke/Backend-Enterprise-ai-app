import markdown
from bs4 import BeautifulSoup


class MarkdownLoader:


    @staticmethod
    def load(
        path: str
    ) -> str:


        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            md = file.read()


        html = markdown.markdown(md)


        soup = BeautifulSoup(
            html,
            "html.parser"
        )


        return soup.get_text()