import streamlit as st
from annotated_text import annotated_text
from mosaico.schema import REAnnotation, WikiPage

from . import BodyRenderer


@BodyRenderer.register("re")
class REBodyRenderer(BodyRenderer):
    async def _render(self, page: WikiPage):
        try:
            re_annotation: REAnnotation = await page.get_annotation("re")
        except KeyError:
            st.write('Annotation "re" missing. Check out json')
            return

        stanza_document = (await page.get_annotation("stanza")).document

        triple_options = []
        option2triple = {}
        for triple in re_annotation.triples:
            option = (
                f"{triple.relation.title}({triple.head.mention}, {triple.tail.mention})"
            )
            triple_options.append(option)
            option2triple[option] = triple

        selected_option = st.selectbox(
            "Choose a relation",
            options=triple_options,
            help="Choose a relation to display",
        )
        triple = option2triple[selected_option]

        document_tokens = []
        for sentence in stanza_document.sentences:
            sentence_tokens = []
            for token in sentence.tokens:
                sentence_tokens.append(token.text)
            document_tokens.append(sentence_tokens)

        labels_to_apply = [
            (
                triple.head.sentence_idx,
                triple.head.token_span,
                triple.head.wikidata_id or "",
                "#B2FF66",
            ),
            (
                triple.tail.sentence_idx,
                triple.tail.token_span,
                triple.tail.wikidata_id or "",
                "#66b2FF",
            ),
        ]

        labels_to_apply = sorted(
            labels_to_apply, key=lambda x: (x[0], x[1][0]), reverse=True
        )

        if range(
            max(labels_to_apply[0][1][0], labels_to_apply[1][1][0]),
            min(labels_to_apply[1][1][1], labels_to_apply[1][1][1]) + 1,
        ):
            st.write(
                "overlap detected between head and tail, renderization currently not supported"
            )
            return

        for s_idx, (t_start, t_end), label, color in labels_to_apply:
            if label == "":
                t_end += 1  # todo TEMPORARY
            text = " ".join(document_tokens[s_idx][t_start:t_end])
            title = label
            if t_start + 1 < t_end:
                del document_tokens[s_idx][t_start + 1 : t_end]

            document_tokens[s_idx][t_start] = (text, title, color)

        for sentence_tokens in document_tokens:
            annotated_text(*[_e for t in sentence_tokens for _e in [t, " "]])
            annotated_text()
