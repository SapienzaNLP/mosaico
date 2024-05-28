<div align="center">
    
# MOSAICo:</br>A Multilingual Open-text Semantically Annotated Interlinked Corpus

[![Conference](http://img.shields.io/badge/NAACL-2024-4b44ce.svg)](https://2024.naacl.org/)
[![Paper](http://img.shields.io/badge/paper-ACL--anthology-B31B1B.svg)]()
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

</div>

## About MOSAICo
This is the repository for the paper [*MOSAICo: a Multilingual Open-text Semantically Annotated Interlinked Corpus*](), presented at NAACL 2024 by [Simone Conia](https://c-simone.github.io/), [Edoardo Barba](https://edobobo.github.io/), Abelardo Carlos Martinez Lorenzo, Pere-Lluís Huguet Cabot, [Riccardo Orlando](https://riccardorlando.xyz/), [Luigi Procopio](https://poccio.github.io/) and [Roberto Navigli](https://www.diag.uniroma1.it/navigli/).

![Mosaico overview](mosaico_overview.png "Mosaico Overview")

### Paper abstract
> Several Natural Language Understanding (NLU) tasks focus on linking text to explicit knowledge, including Word Sense Disambiguation, Semantic Role Labeling, Semantic Parsing, and Relation Extraction.
In addition to the importance of connecting raw text with explicit knowledge bases, the integration of such carefully curated knowledge into deep learning models has been shown to be beneficial across a diverse range of applications, including Language Modeling and Machine Translation. Nevertheless, the scarcity of semantically-annotated corpora across various tasks and languages limits the potential advantages significantly. To address this issue, we put forward MOSAICo, the first endeavor aimed at equipping the research community with the key ingredients to model explicit semantic knowledge at a large scale, providing hundreds of millions of silver yet high-quality annotations for four NLU tasks across five languages. We describe the creation process of MOSAICo, demonstrate its quality and variety, and analyze the interplay between different types of semantic information. MOSAICo, available at https://github.com/SapienzaNLP/mosaico, aims to drop the requirement of closed, licensed datasets and represents a step towards a level playing field across languages and tasks.

* Full paper: [Coming soon (NAACL 2024)!]()

### Cite this work
If you use any part of this work, please consider citing the paper as follows:

```bibtex
@inproceedings{conia-etal-2024-mosaico,
    title     = "{MOSAICo}: a Multilingual Open-text Semantically Annotated Interlinked Corpus",
    author    = "Conia, Simone and Barba, Edoardo and Martinez Lorenzo, Abelardo Carlos and Huguet Cabot, Pere-Lluis and Orlando, Riccardo and Procopio, Luigi and Navigli, Roberto",
    booktitle = "Proceedings of NAACL 2024",
    month     = jun,
    year      = "2024",
    address   = "Mexico City, Mexico",
    publisher = "Association for Computational Linguistics",
}
```

## How is MOSAICo built?
MOSAICo provides high-quality silver annotations for 4 semantic tasks:
* **Word Sense Disambiguation:** we use [ESCHER](https://github.com/SapienzaNLP/esc), a state-of-the-art WSD system adapted for multilingual settings.
* **Semantic Role Labeling:** we use [Multi-SRL](https://github.com/SapienzaNLP/multi-srl), a state-of-the-art multilingual system for dependency- and span-based SRL.
* **Semantic Parsing:** we use [SPRING](https://github.com/SapienzaNLP/spring), a state-of-the-art semantic parser adapted for multilingual settings.
* **Relation Extraction:** we use [mREBEL](https://github.com/Babelscape/rebel?tab=readme-ov-file#REDFM), a state-of-the-art system for multilingual RE.

## Usage

### Set up MongoDB

MOSAICo data are released as *mongoexported* JSON files that can be loaded into a local instance of MongoDB.

First, we need to start a local MongoDB instance (we suggest using Docker):
```bash
docker run \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  -p 27017:27017 \
  --name local-mosaico-db \
  --detach \
  mongo:6.0.11
```

Then, we need to *mongoimport* the data corresponding to three collections.
| Collection | Sample | Full |
| --- | --- | --- |
| interlanguage-links | - | [link](https://drive.google.com/file/d/1pAWoSwf-xiXZZvK4SQMRADIg2zu_Ua1P/view?usp=sharing) |
| pages | [link](https://drive.google.com/file/d/1ZiFeG0sx3rfNS-JQsEIBzAWW1JfLF0Vy/view?usp=sharing) | Coming Soon! |
| annotations | [link](https://drive.google.com/file/d/12equcYN_u06P0HGQILPFDr2ixMAD0v2H/view?usp=sharing) | Coming Soon! |

> The *Sample* column refers to **an English-only sample of 835 annotated documents**. We are finalizing the last details on the entire multilingual release, which will soon be available.

Once downloaded, you can import the data into the local MongoDB instance.
```bash
# import interlanguage links
docker exec -i local-mosaico-db \
    mongoimport \
    --authenticationDatabase admin -u admin -p password \
    --db mosaico --collection interlanguage-links < <path-to-interlanguage-links.collection.json>


# import pages
docker exec -i local-mosaico-db \
    mongoimport \
    --authenticationDatabase admin -u admin -p password \
    --db mosaico --collection pages < <path-to-pages.collection.json>


# import annotations
docker exec -i local-mosaico-db \
    mongoimport \
    --authenticationDatabase admin -u admin -p password \
    --db mosaico --collection annotations < <path-to-annotations.collection.json>
```


### Installing the MOSAICo library

```bash
pip install git+https://github.com/SapienzaNLP/mosaico
```

### Using the MOSAICo library

> **The library heavily uses async programming.** If you cannot integrate that within your code (e.g., inside a torch.Dataset), I suggest using a separate script to download the data locally. Moreover, we built this project on top of [beanie](https://beanie-odm.dev/), an ODM for MongoDB. Before proceeding, we strongly recommend to check out its tutorial, as **WikiPage is a beanie.Document**.

```python
import asyncio
from mosaico.schema import init, WikiPage


async def main():
    await init(
        mongo_uri="mongodb://admin:password@127.0.0.1:27017/",
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

For more information, check out the *examples/* folder. If interested in the fields available for each annotation, check out the pydantic models defined in *src/mosaico/schema/annotations/*.

### Streamlit Demo

This code includes a script to run a streamlit demo that allows for easy data visualization.

```bash
PYTHONPATH=$(pwd) pdm run demo
```

## Working on the library

### Setup Env

This repository uses [PDM](https://pdm-project.org/en/latest/) as its dependency manager.

```bash
# install pdm package manager
curl -sSL https://pdm-project.org/install-pdm.py | python3 -
# and add binary folder to PATH

pdm install
```

### Patch WikiExtractor

We use an alignment algorithm to link the Cirrus text (which **does not** contain metadata such as sections and links) to the standard Wikipedia source text (which **does**).

In this process, we compute a cleaned more-easily-alignable version of the source text by applying [wikiextractor](https://github.com/attardi/wikiextractor). For best results,
we recommend correcting (i.e., patching) the installed version of wikiextractor by updating the following lines in *wikiextractor.extract:clean*:
```python
for tag in discardElements:
    text = dropNested(text, r'<\s*%s\b[^>/]*>' % tag, r'<\s*/\s*%s>' % tag)
```
to:
```python
for tag in discardElements:
    text = dropNested(text, r'<\s*%s\b[^>]*[^/]*>' % tag, r'<\s*/\s*%s>' % tag)
```

The reason behind this change is that the original regex fails on some edge cases:
```
Inspired by the first person ever to be cured of HIV, <a href="The%20Berlin%20Patient">The Berlin Patient</a>, StemCyte began collaborations with <a href="Cord%20blood%20bank">Cord blood bank</a>s worldwide to systematically screen <a href="Umbilical%20cord%20blood">Umbilical cord blood</a> samples for the CCR5 mutation beginning in 2011.<ref name="CCR5Δ32/Δ32 HIV-resistant cord blood"></ref>
```
This is the **cleaned** text returned by the original unpatched function: the trailing *<ref>* hasn't been deleted because */* is excluded by the regex (while it should only be excluded if second to last char).


More details on the linking process can be found in *src/scripts/annotations/source_text_linking/link.py*.

## License
The data is licensed under [Creative Commons Attribution-ShareAlike-NonCommercial 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
