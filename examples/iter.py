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


if __name__ == "__main__":
    asyncio.run(main())
