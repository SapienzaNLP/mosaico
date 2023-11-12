import streamlit as st

from annotated_text import annotated_text

from mosaico.schema import WikiPage
from . import BodyRenderer


@BodyRenderer.register("wsd")
class WSDBodyRenderer(BodyRenderer):
    neutral_color = "#EEEEEE"
    highlight_color = "#FFC300"

    def article2hs_idx_key(self, page: WikiPage):
        language = page.language
        title = page.title
        key = f"{self.__class__.__name__}@{language}@{title}@hs_idx"
        if key not in st.session_state:
            st.session_state[key] = 0
        return key

    def article2ha_idx_key(self, page: WikiPage):
        language = page.language
        title = page.title
        key = f"{self.__class__.__name__}@{language}@{title}@ha_idx"
        if key not in st.session_state:
            st.session_state[key] = 0
        return key

    async def _render(self, page: WikiPage):
        try:
            wsd_annotation = await page.get_annotation("wsd")
        except KeyError:
            st.write('Annotation "wsd" missing. Check out json')
            return

        stanza_document = (await page.get_annotation("stanza")).document

        col1, col2 = st.columns(2)

        def back_sentence():
            st.session_state[self.article2hs_idx_key(page)] -= 1
            st.session_state[self.article2ha_idx_key(page)] = 0

        def next_sentence():
            st.session_state[self.article2hs_idx_key(page)] += 1
            st.session_state[self.article2ha_idx_key(page)] = 0

        def back_annotation():
            st.session_state[self.article2ha_idx_key(page)] -= 1

        def next_annotation():
            st.session_state[self.article2ha_idx_key(page)] += 1

        with col1:
            st.button(
                "[Sentence] Back",
                on_click=back_sentence,
                disabled=st.session_state[self.article2hs_idx_key(page)] == 0,
                help=f'Show previous sentence for language "{page.language}"',
            )
            st.button(
                "[Annotation] Back",
                on_click=back_annotation,
                disabled=st.session_state[self.article2ha_idx_key(page)] == 0,
                help=f'Show previous annotation for language "{page.language}"',
            )

        with col2:
            st.button(
                "[Sentence] Next",
                on_click=next_sentence,
                disabled=st.session_state[self.article2hs_idx_key(page)]
                == len(stanza_document.sentences) - 1,
                help=f'Show next sentence for language "{page.language}"',
            )

            st.button(
                "[Annotation] Next",
                on_click=next_annotation,
                disabled=(
                    wsd_annotation.document_spans[
                        st.session_state[self.article2hs_idx_key(page)]
                    ]
                    == []
                    or st.session_state[self.article2ha_idx_key(page)]
                    == len(
                        wsd_annotation.document_spans[
                            st.session_state[self.article2hs_idx_key(page)]
                        ]
                    )
                    - 1
                ),
                help=f'Show next annotation for language "{page.language}"',
            )

        # get current idxs
        highlighted_sentence_idx = st.session_state[self.article2hs_idx_key(page)]
        highlighted_annotation_idx = st.session_state[self.article2ha_idx_key(page)]

        if wsd_annotation.document_spans[highlighted_sentence_idx] == []:
            st.markdown(
                f"""<p style="color:lightgray">{stanza_document.sentences[highlighted_sentence_idx].text}</p>""",
                unsafe_allow_html=True,
            )
            return

        sentence_tokens = []
        for token in stanza_document.sentences[highlighted_sentence_idx].tokens:
            sentence_tokens.append(token.text)

        labels_to_apply = []
        for annotation_idx, annotation in enumerate(
            wsd_annotation.document_spans[highlighted_sentence_idx]
        ):
            labels_to_apply.append(
                (
                    annotation.token_span,
                    annotation.label,
                    self.highlight_color
                    if highlighted_annotation_idx == annotation_idx
                    else self.neutral_color,
                )
            )

        highlighted_label = labels_to_apply[highlighted_annotation_idx][1]
        labels_to_apply = sorted(
            labels_to_apply, key=lambda x: (x[0], x[1][0]), reverse=True
        )

        for (t_start, t_end), label, color in labels_to_apply:
            text = " ".join(sentence_tokens[t_start:t_end])
            title = label

            if t_start + 1 < t_end:
                del sentence_tokens[t_start + 1 : t_end]

            sentence_tokens[t_start] = (text, title, color)

        annotated_text(*[_e for t in sentence_tokens for _e in [t, " "]])
        annotated_text()

        st.markdown("---")

        st.components.v1.iframe(
            f"https://babelnet.org/synset?id={highlighted_label}&lang=EN",
            height=600,
            scrolling=True,
        )
