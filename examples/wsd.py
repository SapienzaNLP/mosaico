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

    stanza_document = (await page.get_annotation("stanza")).document
    wsd_annotation = await page.get_annotation("wsd")

    sentence_idx = 1
    tokens = [t.text for t in stanza_document.sentences[sentence_idx].tokens]

    print(stanza_document.sentences[sentence_idx].text)
    for sentence_span in wsd_annotation.document_spans[sentence_idx]:
        text = " ".join(
            tokens[sentence_span.token_span[0] : sentence_span.token_span[1]]
        )
        print(
            f"* {sentence_span.token_span[0]} - {sentence_span.token_span[1]}: {text} => {sentence_span.label}"
        )


if __name__ == "__main__":
    asyncio.run(main())
