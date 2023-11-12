import collections

import streamlit as st

try:
    from annotated_text import annotated_text
except ModuleNotFoundError:
    print(
        "Package st-annotated-text not installed. Please install it: 'pip install st-annotated-text'"
    )
    exit(1)

from mosaico.schema import WikiPage
from mosaico.schema.annotations.stanza import _pos_classes as pos_classes
from . import BodyRenderer, color_iterator


@BodyRenderer.register("stanza")
class StanzaBodyRenderer(BodyRenderer):
    color_it = color_iterator()
    pos2color = collections.defaultdict(lambda: next(StanzaBodyRenderer.color_it))

    @staticmethod
    def _render_sidebar_kwargs() -> dict:
        shown_pos = st.sidebar.multiselect("Choose displayed POS", pos_classes)
        display_lemma = st.sidebar.checkbox("Display lemma")
        return dict(shown_pos=shown_pos, display_lemma=display_lemma)

    def __init__(self, shown_pos: list, display_lemma: bool):
        self.shown_pos = set(shown_pos)
        self.display_lemma = display_lemma

    async def _render(self, page: WikiPage):
        stanza_document = (await page.get_annotation("stanza")).document

        for sentence_idx, sentence in enumerate(stanza_document.sentences):
            st.markdown(
                f"""<p style="color:lightgray">[{page.document_id}.{sentence_idx}]</p>""",
                unsafe_allow_html=True,
            )

            tokens = []

            for token in sentence.tokens:
                text, pos, lemma = token.text, token.pos, token.lemma

                if pos in self.shown_pos:
                    label = f"{pos} -- {lemma}" if self.display_lemma else pos
                    tokens.append((text, label, StanzaBodyRenderer.pos2color[pos]))
                else:
                    tokens.append(text)

                tokens.append(" ")

            annotated_text(*tokens)
            annotated_text()


@BodyRenderer.register("stanza-ner")
class StanzaNERBodyRenderer(BodyRenderer):
    color_it = color_iterator()
    ner2color = collections.defaultdict(lambda: next(StanzaNERBodyRenderer.color_it))

    async def _render(self, page: WikiPage):
        stanza_document = (await page.get_annotation("stanza")).document

        for sentence in stanza_document.sentences:
            # extract tokens and labels
            tokens, labels = [], []
            for token in sentence.tokens:
                tokens.append(token.text)
                labels.append(token.ner)

            # process bio annotation
            grouped_tokens, grouped_labels = [], []
            for t, l in zip(tokens, labels):
                if l.startswith("I") or l.startswith("E"):
                    grouped_tokens[-1] += f" {t}"
                else:
                    grouped_tokens.append(t)
                    grouped_labels.append(None if l == "O" else l[2:])

            assert len(grouped_tokens) == len(grouped_labels)

            # write
            annotated_text(
                *[
                    _e
                    for t, l in zip(grouped_tokens, grouped_labels)
                    for _e in [
                        (t, l, StanzaNERBodyRenderer.ner2color[l])
                        if l is not None
                        else t,
                        " ",
                    ]
                ]
            )
            annotated_text()
