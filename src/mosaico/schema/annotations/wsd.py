from typing import ClassVar

from pydantic import BaseModel

from .base import Annotation


class WSDSpanAnnotation(BaseModel):
    token_span: tuple[int, int]
    label: str


class WSDAnnotation(Annotation):
    name: ClassVar[str] = "wsd"
    document_spans: list[list[WSDSpanAnnotation]]
