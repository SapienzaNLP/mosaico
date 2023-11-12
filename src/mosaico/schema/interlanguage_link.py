from beanie import Document, PydanticObjectId
from enum import Enum
from pymongo import IndexModel

from pydantic import BaseModel


class Language(str, Enum):
    EN = "en"
    IT = "it"
    ES = "es"
    FR = "fr"
    DE = "de"


class InterlanguageLink(Document):
    class PageLink(BaseModel):
        language: str
        page_id: PydanticObjectId

    wikidata_id: str
    page_links: list[PageLink] = []

    @classmethod
    async def get_or_insert(cls, wikidata_id: str):
        interlanguage_link = await InterlanguageLink.find_one(
            InterlanguageLink.wikidata_id == wikidata_id
        )

        if interlanguage_link is None:
            interlanguage_link = InterlanguageLink(wikidata_id=wikidata_id)
            await interlanguage_link.insert()

        return interlanguage_link

    async def add_page(self, page: "WikiPage"):
        self.page_links.append(
            InterlanguageLink.PageLink(language=page.language, page_id=page.id)
        )
        await self.save()

    class Settings:
        name = "interlanguage-links"
        indexes = [
            IndexModel("wikidata_id", unique=True),
        ]
        use_revision = True
        keep_nulls = False
