# MOSAICO Library Examples

In all examples, we assume that the script is invoked with the environment variable MONGO_URI set. This can be achieved either by exporting the variable or by providing it to the script itself:

```bash
# exporting it
export MONGO_URI="<mongo-uri>"
python [...]

# providing it to the script
MONGO_URI="<mongo-uri>" python [...]
```

* **simple.py**: simple script showing basic library usage
* **projection.py**: script showing the usage of projections. A projection in MongoDB is simply a mean to specify we are interested in only a specific subset of data and that only that subset should be fetched. Depending on the projection, **this can massively boost** your querying speed. However, **be careful on what you include in your projection model**, as some annotations depend on page fields / the availability of other annotations.
* **iter.py**: script showing how to iterate on all (or all those matching a query) in the DB.
* **stanza.py**: showcase of the [Stanza](https://stanfordnlp.github.io/stanza/) annotation.
* **wsd.py**: showcase of the Word Sense Disambiguation (WSD) annotation.
* **srl.py**: showcase of the Semantic Role Labeling (SRL) annotation.
* **rel_ex.py**: showcase of the Relation Extraction (RE) annotation.
* **amr.py**: showcase of the Abstract Meaning Representation (AMR) annotation.
