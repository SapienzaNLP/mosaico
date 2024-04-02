import asyncio
import os

from mosaico.schema import WikiPage, init


async def main():
    await init(
        mongo_uri=os.environ["MONGO_URI"],
        db="mosaico",
    )

    page = await WikiPage.find_one(WikiPage.title == "Barack Obama")

    stanza_document = (await page.get_annotation("stanza")).document
    srl_annotation = await page.get_annotation("srl")

    print(stanza_document.sentences[0].text)
    tokens = [t.text for t in stanza_document.sentences[0].tokens]

    for pred_arg_structure in srl_annotation.inventory2document_spans["propbank"][0]:
        print(
            f"* {tokens[pred_arg_structure.predicate.token_idx]} => {pred_arg_structure.predicate.label}"
        )
        for argument in pred_arg_structure.arguments:
            if argument.role != "V":
                print(
                    f"  - {' '.join(tokens[argument.start: argument.end])} => {argument.role}"
                )


if __name__ == "__main__":
    asyncio.run(main())
