# MoSAICo


## Open Issues

* Source text linking coverage (impacts on sectioning and wikilinks)
* Propagations bug on wikilinks

## Installing the library

```bash
pip install git+https://github.com/SapienzaNLP/mosaico
```

## Using the library

> **The library heavily uses async programming.** If you cannot integrate that within your code (e.g., inside a torch.Dataset), I suggest using a separate script to download the data locally. Moreover, we built this project on top of [beanie](https://beanie-odm.dev/), an ODM for Mongo. Before proceeding, we strongly recommend to check out its tutorial, as **WikiPage is a beanie.Document**.

```python
import asyncio
from mosaico.schema import init, WikiPage


async def main():
    await init(
        mongo_uri="mongodb://<your user>:<your password>@<the ip:port where you'll reach Mongo>",
        db="mosaico",
    )

    page = await WikiPage.find_one(WikiPage.title == "Barack Obama")
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
```

For more information, check out the *examples/* folder.

## Streamlit Demo

```bash
export MONGO_URI="mongodb://<your user>:<your password>@<the ip:port where you'll reach Mongo>"

PYTHONPATH=$(pwd) \
    streamlit \
    run \
    src/scripts/demo/main.py \
    --server.headless True
```
