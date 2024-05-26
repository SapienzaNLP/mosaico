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

    re_triples = (await page.get_annotation("re")).triples
    stanza_document = (await page.get_annotation("stanza")).document

    for triple in re_triples:
        print(
            f"[{triple.annotator}] {triple.relation.title} [wikidata={triple.relation.wikidata_id}]"
        )
        print(f"  * head: {triple.head.mention} [wikidata={triple.head.wikidata_id}]")
        print(f"  * tail: {triple.tail.mention} [wikidata={triple.tail.wikidata_id}]")
        print()
        print(
            " ".join(
                [
                    s.text
                    for s in stanza_document.sentences[
                        triple.origin.sentence_span[0] : triple.origin.sentence_span[1]
                    ]
                ]
            )
        )
        print()
        break


if __name__ == "__main__":
    asyncio.run(main())
