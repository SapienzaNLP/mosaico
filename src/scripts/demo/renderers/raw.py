from . import BodyRenderer
import streamlit as st

from mosaico.schema import WikiPage


@BodyRenderer.register("raw-json")
class RawJSONBodyRenderer(BodyRenderer):
    async def _render(self, page: WikiPage):
        for linked_annotation_name in page.linked_annotation_names:
            await page.get_annotation(linked_annotation_name)

        st.json(
            dict(
                base=dict(
                    language=page.language,
                    title=page.title,
                    text=page.text,
                    document_id=page.document_id,
                    wikidata_id=page.wikidata_id,
                ),
                annotations={
                    annotation.name: annotation.model_dump()
                    async for annotation in page.list_annotations()
                },
            ),
            expanded=False,
        )
