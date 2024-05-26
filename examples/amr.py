import asyncio
import os

from mosaico.schema import Language, WikiPage, init


async def main():
    await init(
        mongo_uri=os.environ["MONGO_URI"],
        db="mosaico",
    )

    page = await WikiPage.find_one(
        WikiPage.language == Language.EN, WikiPage.title == "Velites"
    )

    amr_graphs = (await page.get_annotation("amr")).sentence_graphs
    stanza_sentences = (await page.get_annotation("stanza")).document.sentences

    for s, g in zip(stanza_sentences, amr_graphs):
        print("##########\n" + "# stanza #\n" + "##########")
        print(s.text)
        print()

        print("#######\n" + "# amr #\n" + "#######")
        print(g.penman)
        break


if __name__ == "__main__":
    asyncio.run(main())
