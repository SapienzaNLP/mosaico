import asyncio
import os

from mosaico.schema import Language, WikiPage, init


async def main():
    await init(
        mongo_uri=os.environ["MONGO_URI"],
        db="mosaico",
    )

    page = await WikiPage.find_one(
        WikiPage.language == Language.EN, WikiPage.title == "Barack Obama"
    )

    print(f"# document id: {page.document_id}")
    print(
        f"# wikidata id: {page.wikidata_id if page.wikidata_id is not None else '<not available>'}"
    )
    print(f"# language: {page.language.value}")
    print(f"# text: {page.text[: 100]} [...]")

    print("# available annotations:")
    async for annotation in page.list_annotations():
        print(f"  * {annotation.name}")

    print("# available translated pages:")
    async for translated_page in page.list_translations():
        print(f"  * {translated_page.language.value} => {translated_page.document_id}")


if __name__ == "__main__":
    asyncio.run(main())
