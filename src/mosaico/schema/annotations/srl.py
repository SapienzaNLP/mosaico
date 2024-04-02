from typing import ClassVar

from pydantic import BaseModel

from .base import Annotation


class PredArgStructure(BaseModel):
    class Argument(BaseModel):
        start: int
        end: int
        role: str

    class Predicate(BaseModel):
        token_idx: int
        label: str

    predicate: Predicate
    arguments: list[Argument]


class SRLAnnotation(Annotation):
    name: ClassVar[str] = "srl"
    inventory2document_spans: dict[str, list[list[PredArgStructure]]]
