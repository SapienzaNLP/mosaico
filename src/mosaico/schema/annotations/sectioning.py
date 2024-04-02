from typing import ClassVar, Optional

from pydantic import BaseModel

from ..interlanguage_link import Language
from .base import Annotation


class OldSection(BaseModel):
    # TODO delete
    name: str
    sentences_span: tuple[int, int]


class Paragraph(BaseModel):
    cleaned_source_text_span: tuple[int, int]
    sentence_span: tuple[int, int]


class Section(BaseModel):
    name: str
    depth: int
    cleaned_source_text_span: tuple[int, int] | None = None
    sentence_span: tuple[int, int] | None = None
    paragraphs: list[Paragraph] | None = None


class SectioningAnnotation(Annotation):
    BLACKLIST_SECTIONS: ClassVar[dict] = {
        Language.EN: [
            "See also",
            "Notes",
            "External links",
            "Further reading",
            "References",
        ],
        Language.DE: [
            "Literatur",
            "Weblinks",
            "Einzelnachweise",
            "Siehe auch",
        ],
        Language.FR: [
            "Voir aussi",
            "Annexes",
            "Liens externes",
            "Notes et références",
        ],
        Language.IT: [
            "Vedi anche",
            "Collegamenti esterni",
            "Bibliografia",
            "Voci correlate",
            "Note",
        ],
        Language.ES: [
            "Véase también",
            "Referencias",
            "Enlaces externos",
            "Bibliografía",
        ],
    }

    name: ClassVar[str] = "sectioning"

    sections: list[Section | OldSection]  # TODO delete OldSection
