import streamlit as st
from mosaico.schema import WikiPage

from . import BodyRenderer


@BodyRenderer.register("amr")
class AMRBodyRenderer(BodyRenderer):
    async def _render(self, page: WikiPage):
        try:
            amr_annotation = await page.get_annotation("amr")
        except KeyError:
            st.write('Annotation "amr" missing. Check out json')
            return

        stanza_document = (await page.get_annotation("stanza")).document
        sentences_text = [sentence.text for sentence in stanza_document.sentences]

        amrs = {}
        for i, graph in enumerate(amr_annotation.sentence_graphs):
            amrs[i] = graph.penman if graph is not None else None

        for i, sentence_text in enumerate(sentences_text):
            st.write(sentence_text)
            if i in amrs:
                st.text(amrs[i])
            st.write("---")
