import asyncio
import os
from mosaico.schema import init, WikiPage, Language
from pydantic import BaseModel
from typing import Optional


class ProjectionModel(BaseModel):
    language: Language
    document_id: str
    wikidata_id: Optional[str] = None


async def main():
    await init(
        mongo_uri=os.environ["MONGO_URI"],
        db="mosaico",
    )

    page = await WikiPage.find_one(
        WikiPage.title == "Barack Obama", projection_model=ProjectionModel
    )
    print(f"# document id: {page.document_id}")
    print(
        f"# wikidata id: {page.wikidata_id if page.wikidata_id is not None else '<not available>'}"
    )
    print(f"# language: {page.language.value}")


if __name__ == "__main__":
    asyncio.run(main())
