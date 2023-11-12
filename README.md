# MoSAICo


## Open Issues

* Source text linking coverage (impacts on sectioning and wikilinks)
* Propagations bug on wikilinks

## Using the library

**The library heavily uses async programming. If you cannot integrate that within your code (e.g., inside a torch.Dataset), I suggest using a separate script to download the data locally**.

```python
import asyncio
import os
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

### Demo

```bash
export MONGO_URI="mongodb://<your user>:<your password>@<the ip:port where you'll reach Mongo>"

PYTHONPATH=$(pwd) \
    streamlit \
    run \
    src/scripts/demo/main.py \
    --server.headless True
```

## Working the library

### Spawn the DB

```bash
# spawn
mkdir -p data/mongo-db
docker run \
    -e MONGO_INITDB_ROOT_USERNAME=<user> \
    -e MONGO_INITDB_ROOT_PASSWORD=<password> \
    -v $(pwd)/data/mongo-db/:/data/db \
    -p 37017:27017 \
    --name mosaico-db \
    -d mongo:6.0.11

# create users
mongosh --authenticationDatabase admin -u <admin-user> -p <admin-pwd>

    use admin

    # create admin
    db.createUser(
        { 
            user: "<user>",
            pwd: passwordPrompt(),
            roles: [ 
                { role: "clusterAdmin", db: "admin" },
                { role: "readWriteAnyDatabase", db: "admin" }
            ]
        }
    )

    ## create readwriteany user
    db.createUser(
        { 
            user: "<user>",
            pwd: passwordPrompt(),
            roles: [
                { role: "readWriteAnyDatabase", db: "admin" }
            ]
        }
    )

    # create read-only db-specific users
    db.createUser(
        { 
            user: "<user>",
            pwd: passwordPrompt(),
            roles: [
                { role: "read", db: "mosaico" },
            ]
        }
    )

    db.createUser(
        { 
            user: "sapnlp-guest",
            pwd: passwordPrompt(),
            roles: [
                { role: "read", db: "mosaico" },
            ]
        }
    )

    # create read-write db-specific users
    db.createUser(
        { 
            user: "<user>",
            pwd: passwordPrompt(),
            roles: [
                { role: "readWrite", db: "mosaico" },
            ]
        }
    )
```