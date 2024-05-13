import asyncio
import os

from mosaico.schema import Language, WikiPage, init


async def main():
    await init(
        mongo_uri=os.environ["MONGO_URI"],
        db="mosaico",
    )

    print("# iterate on all pages, printing the title of the first five of them:")
    async for page in WikiPage.find(limit=5):
        print(f"  * {page.title}")
    print()

    print(
        "# iterate on all pages whose language is English, printing the title of the first five of them:"
    )
    async for page in WikiPage.find(WikiPage.language == Language.EN, limit=5):
        print(f"  * {page.title}")
    print()

    print(
        "# iterate on all pages in mosaico core, printing the title of the first five of them:"
    )
    async for page in WikiPage.find({"is_mosaico_core": True}, limit=5):
        print(f"  * {page.title}")

    print(
        "# iterate on all pages in English that contain WSD annotations, printing the title of the first five of them:"
    )
    async for page in WikiPage.find(
        WikiPage.language == "en",
        {"materialized_annotations.name": "wsd"},
        limit=5,
    ):
        print(f"  * {page.title}")

    print(
        "# iterate on all pages in English that contain either WSD or SRL annotations, printing the title of the first five of them:"
    )
    async for page in WikiPage.find(
        WikiPage.language == "en",
        {
            "$or": [
                {"materialized_annotations.name": "srl"},
                {"materialized_annotations.name": "wsd"},
            ]
        },
        limit=5,
    ):
        print(f"  * {page.title}")


if __name__ == "__main__":
    asyncio.run(main())
