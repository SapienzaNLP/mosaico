from enum import Enum
from typing import ClassVar

from pydantic import BaseModel

from ..wikipage import WikiPage
from .base import Annotation


class Origin(BaseModel):
    paragraph_idx: int | None = None
    sentence_span: tuple[int, int]


class Annotator(str, Enum):
    WSD = "wsd"
    CROCODILE = "crocodile"
    RELIK = "relik"


class Relation(BaseModel):
    title: str
    wikidata_id: str | None = None


class Argument(BaseModel):
    sentence_idx: int
    token_span: tuple[int, int]

    wikidata_id: str | None = None

    _mention: str | None = None

    async def _prepare_with_page(self, page: WikiPage):
        sentence_tokens = (
            (await page.get_annotation("stanza"))
            .document.sentences[self.sentence_idx]
            .tokens
        )
        start_token, end_token = (
            sentence_tokens[self.token_span[0]],
            sentence_tokens[self.token_span[-1] - 1],
        )
        self._mention = page.text[start_token.char_start : end_token.char_end]

    @property
    def mention(self) -> str:
        return self._mention


class RETriple(BaseModel):
    origin: Origin
    annotator: Annotator

    relation: Relation
    head: Argument
    tail: Argument

    async def _prepare_with_page(self, page: WikiPage):
        await self.head._prepare_with_page(page)
        await self.tail._prepare_with_page(page)


class REAnnotation(Annotation):
    name: ClassVar[str] = "re"
    triples: list[RETriple]

    async def _prepare_with_page(self, page: WikiPage):
        for triple in self.triples:
            await triple._prepare_with_page(page)
