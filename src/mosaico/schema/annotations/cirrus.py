from .base import Annotation

from typing import Any, ClassVar


class CirrusAnnotation(Annotation):
    name: ClassVar[str] = "cirrus"
    data: dict[str, Any]
