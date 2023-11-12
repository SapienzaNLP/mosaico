import asyncio
import os
from mosaico.schema import init, WikiPage


async def main():
    await init(
        mongo_uri=os.environ["MONGO_URI"],
        db="mosaico",
    )

    page = await WikiPage.find_one(WikiPage.title == "Barack Obama")

    stanza_document = (await page.get_annotation("stanza")).document
    for token in stanza_document.sentences[0].tokens:
        print(f"* {token.text} -- ({token.pos}, {token.lemma}, {token.morph})")


if __name__ == "__main__":
    asyncio.run(main())
