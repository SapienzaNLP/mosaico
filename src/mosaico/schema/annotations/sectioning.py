from typing import ClassVar

from pydantic import BaseModel
from .base import Annotation


class Section(BaseModel):
    name: str
    sentences_span: tuple[int, int]


class SectioningAnnotation(Annotation):
    name: ClassVar[str] = "sectioning"

    sections: list[Section]
