from beanie import Document, Link
from pymongo import IndexModel
from pydantic import model_validator
import logging
from typing import Iterator, Optional
from .annotations import (
    Annotation,
    MaterializedAnnotationContainer,
    LinkedAnnotationContainer,
)
import zlib
from bson import Binary
from .interlanguage_link import Language, InterlanguageLink


class WikiPage(Document):
    document_id: str
    wikidata_id: Optional[str] = None
    title: str
    language: Language

    compressed_text: Binary | bytes
    _text: Optional[str] = None

    materialized_annotations: list[MaterializedAnnotationContainer] = []
    linked_annotation_names: list[str] = []
    linked_annotations: list[Link[LinkedAnnotationContainer]] = []

    _annotations: dict[str, Annotation | Link[Annotation]] = {}

    @model_validator(mode="before")
    def handle_text_compression(cls, data: dict):
        if "compressed_text" not in data:
            assert "text" in data
            data["compressed_text"] = Binary(zlib.compress(data["text"].encode()))

        return data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for ma in self.materialized_annotations:
            self._annotations[ma.name] = ma.annotation
        for lan, la in zip(self.linked_annotation_names, self.linked_annotations):
            self._annotations[lan] = la

    @property
    def text(self) -> str:
        if self._text is None:
            self._text = zlib.decompress(self.compressed_text).decode()
        return self._text

    @property
    def link(self) -> str:
        return f"https://{self.language.value}.wikipedia.org/wiki/{self.title.replace(' ', '_')}"

    def add_annotation(self, annotation: Annotation, materialized: bool = True):
        if materialized:
            self.materialized_annotations.append(
                MaterializedAnnotationContainer.from_annotation(annotation)
            )
        else:
            self.linked_annotation_names.append(annotation.name)
            self.linked_annotations.append(
                LinkedAnnotationContainer.from_annotation(annotation)
            )

        self._annotations[annotation.name] = annotation

    async def get_annotation(self, name: str):
        if name not in self._annotations:
            raise KeyError(f"No annotation {name} present")
        elif isinstance(self._annotations[name], Link):
            logging.info(f"Following href in DB to retrieve annotation {name}")
            link_annotation = await self._annotations[name].fetch()
            self._annotations[name] = link_annotation.annotation

        if not self._annotations[name].prepared:
            await self._annotations[name].prepare_with_page(self)

        return self._annotations[name]

    async def list_annotations(self) -> Iterator[Annotation]:
        for name in self._annotations:
            annotation = await self.get_annotation(name)
            yield annotation

    async def change_to_translation(self, language: Language) -> "WikiPage":
        interlanguage_link = InterlanguageLink.find(
            InterlanguageLink.wikidata_id == self.wikidata_id
        )

        for page_link in interlanguage_link.page_links:
            if page_link.language == language:
                return await WikiPage.get(page_link.page_id)

        raise KeyError(language)

    async def list_translations(self) -> Iterator["WikiPage"]:
        interlanguage_link = await InterlanguageLink.find_one(
            InterlanguageLink.wikidata_id == self.wikidata_id
        )

        for page_link in interlanguage_link.page_links:
            if page_link.language != self.language:
                yield await WikiPage.get(page_link.page_id)

    class Config:
        arbitrary_types_allowed = True

    class Settings:
        name = "pages"
        indexes = [
            IndexModel("wikidata_id", sparse=True),
            IndexModel(["title", "language"], unique=True),
            IndexModel(["document_id", "language"], unique=True),
        ]
        use_revision = True
        keep_nulls = False
