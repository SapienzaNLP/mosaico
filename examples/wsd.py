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
    wsd_annotation = await page.get_annotation("wsd")
    tokens = [t.text for t in stanza_document.sentences[0].tokens]

    print(stanza_document.sentences[0].text)
    for sentence_span in wsd_annotation.document_spans[0]:
        text = " ".join(
            tokens[sentence_span.token_span[0] : sentence_span.token_span[1]]
        )
        print(
            f"* {sentence_span.token_span[0]} - {sentence_span.token_span[1]}: {text} => {sentence_span.label}"
        )


if __name__ == "__main__":
    asyncio.run(main())
