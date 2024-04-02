from typing import Any, ClassVar

from beanie import Document
from pydantic import (
    BaseModel,
    ValidationInfo,
    field_validator,
)
from pymongo import IndexModel


class Annotation(BaseModel):
    name: ClassVar[str]
    registry: ClassVar[dict] = {}

    _prepared: bool = False

    @property
    def prepared(self):
        return self._prepared

    @prepared.setter
    def prepared(self, value: bool):
        self._prepared = value

    def __init_subclass__(cls, **kwargs):
        r = super().__init_subclass__(**kwargs)
        assert cls.name not in cls.registry
        cls.registry[cls.name] = cls
        return r

    async def prepare_with_page(self, page: "WikiPage"):
        await self._prepare_with_page(page)
        self.prepared = True

    async def _prepare_with_page(self, page: "WikiPage"):
        pass


class AnnotationContainer(BaseModel):
    name: str
    annotation: Annotation

    @classmethod
    def from_annotation(cls, annotation: Annotation):
        return cls(name=annotation.name, annotation=annotation)

    @field_validator("annotation", mode="before")
    def identify_and_instantiate_subclass(
        cls, annotation: Any, validation_info: ValidationInfo
    ):
        if isinstance(annotation, dict):
            annotation = Annotation.registry[validation_info.data["name"]](**annotation)
        return annotation


class MaterializedAnnotationContainer(AnnotationContainer):
    pass


class LinkedAnnotationContainer(Document, AnnotationContainer):
    class Settings:
        name = "annotations"
        indexes = [IndexModel("annotation.name")]
        use_revision = True
