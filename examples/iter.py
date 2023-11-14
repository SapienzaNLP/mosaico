import asyncio
import os
from mosaico.schema import init, WikiPage, Language


async def plain_iter():
    print("# plain iter:")
    async for page in WikiPage.find(limit=5):
        print(f"* {page.title}")


async def main():
    await init(
        mongo_uri=os.environ["MONGO_URI"],
        db="mosaico",
    )

    print("# iterate on all pages, printing the title of the first five of them:")
    async for page in WikiPage.find(limit=5):
        print(f"  * {page.title}")

    print(
        "# iterate on all pages whose language is English, printing the title of the first five of them:"
    )
    async for page in WikiPage.find(WikiPage.language == Language.EN, limit=5):
        print(f"  * {page.title}")


if __name__ == "__main__":
    asyncio.run(main())
