from typing import ClassVar

from pydantic import BaseModel

from .base import Annotation


class AMRGraph(BaseModel):
    penman: str


class AMRAnnotation(Annotation):
    name: ClassVar[str] = "amr"
    sentence_graphs: list[AMRGraph | None]
