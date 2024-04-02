from typing import ClassVar, Optional

from pydantic import BaseModel

from .base import Annotation


class ProjectedWikilink(BaseModel):
    sentence_idx: int
    token_span: tuple[int, int]
    mention: str
    title: str
    wikidata_id: Optional[str] = None
    bn_id: Optional[str] = None
    wn_id: Optional[str] = None
    wn_sense: Optional[str] = None
    propagated_spans: Optional[list[tuple[int, tuple[int, int], str]]] = None


class MissedWikilink(BaseModel):
    mention: str
    title: str
    source_text_span: tuple[int, int]
    last_match: Optional[tuple[int, tuple[int, int]]] = None


class Wikilink(BaseModel):
    sentence_idx: int
    token_span: tuple[int, int]
    mention: str
    title: str
    wikidata_id: Optional[str] = None
    bn_id: Optional[str] = None
    wn_id: Optional[str] = None
    wn_sense: Optional[str] = None
    propagated_spans: Optional[list[tuple[int, tuple[int, int], str]]] = None


class WikilinksAnnotation(Annotation):
    name: ClassVar[str] = "wikilinks"

    wikilinks: Optional[list[Wikilink]] = None  # TODO remove Optional
    projected_wikilinks: Optional[list[ProjectedWikilink]] = None  # TODO remove
    missed_wikilinks: Optional[list[MissedWikilink]] = None  # TODO remove
