from typing import Any, ClassVar

from wikiextractor.extract import Extractor, clean

from .base import Annotation


class CirrusAnnotation(Annotation):
    name: ClassVar[str] = "cirrus"
    data: dict[str, Any]

    @property
    def source_text(self):
        return self.data["source_text"]

    @property
    def cleaned_source_text(self):
        Extractor.keepLinks = True
        return clean(
            Extractor(
                id=None, revid=None, urlbase=None, title=self.data["title"], page=None
            ),
            self.data["source_text"],
            expand_templates=False,
            html_safe=False,
        )
