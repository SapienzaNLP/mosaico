import html

import streamlit as st
from annotated_text import annotated_text
from mosaico.schema import Wikilink, WikiPage

from . import BodyRenderer, brighten_color


@BodyRenderer.register("wikipage")
class WikipageBodyRenderer(BodyRenderer):
    async def _render(self, page: WikiPage):
        st.components.v1.iframe(
            page.link,
            height=900,
            scrolling=True,
        )


@BodyRenderer.register("cirrus")
class CirrusBodyRenderer(BodyRenderer):
    @staticmethod
    def _render_sidebar_kwargs() -> dict:
        show_categories = st.sidebar.checkbox("Show categories")
        return dict(show_categories=show_categories)

    def __init__(self, show_categories: bool):
        self.show_categories = show_categories

    async def _render(self, page: WikiPage):
        if self.show_categories:
            st.subheader("Categories")
            categories = (await page.get_annotation("cirrus")).data["category"]
            cols = st.columns(3)
            for i in range(len(categories)):
                with cols[i % 3]:
                    st.markdown(f"* {categories[i]}")
            st.markdown("---")
        st.write(html.escape(page.text))


@BodyRenderer.register("source-text")
class SourceTextRenderer(BodyRenderer):
    @staticmethod
    def _render_sidebar_kwargs() -> dict:
        show_cleaned_text = st.sidebar.checkbox("Show cleaned text")
        return dict(show_cleaned_text=show_cleaned_text)

    def __init__(self, show_cleaned_text: bool):
        self.show_cleaned_text = show_cleaned_text

    async def _render(self, page: WikiPage):
        if self.show_cleaned_text:
            st.write((await page.get_annotation("cirrus")).cleaned_source_text)
        else:
            st.write((await page.get_annotation("cirrus")).source_text)


@BodyRenderer.register("section")
class SectionBodyRenderer(BodyRenderer):
    async def _render(self, page: WikiPage):
        sectioning_annotation = await page.get_annotation("sectioning")
        stanza_document = (await page.get_annotation("stanza")).document
        stanza_sentences, i = stanza_document.sentences, 0

        for section in sectioning_annotation.sections:
            if section.sentence_span is None:
                continue

            # re-align
            while i < section.sentence_span[0]:
                st.markdown(f":red[{stanza_sentences[i].text}]")
                i += 1

            st.markdown(f"#{'#' * section.depth} {section.name}")

            for paragraph in section.paragraphs or []:
                # re-align
                while i < paragraph.sentence_span[0]:
                    st.markdown(f":red[{stanza_sentences[i].text}]")
                    i += 1

                st.write(
                    " ".join(
                        [
                            stanza_sentences[j].text
                            for j in range(
                                paragraph.sentence_span[0], paragraph.sentence_span[1]
                            )
                        ]
                    )
                    + "\n"
                )
                i += paragraph.sentence_span[1] - paragraph.sentence_span[0]

            # re-align
            while i < section.sentence_span[1]:
                st.markdown(f":red[{stanza_sentences[i].text}]")
                i += 1

            st.markdown("---")

        # re-align
        while i < len(stanza_sentences):
            st.markdown(f":red[{stanza_sentences[i].text}]")
            i += 1


@BodyRenderer.register("wikilinks")
class WikilinkBodyRenderer(BodyRenderer):
    @staticmethod
    def _render_sidebar_kwargs() -> dict:
        show_propagations = st.sidebar.checkbox("Show propagations")
        show_link = st.sidebar.selectbox(
            "Select label type", options=["Title", "Wikidata", "BabelNet", "WordNet"]
        )
        return dict(show_propagations=show_propagations, show_link=show_link)

    def __init__(self, show_propagations: bool, show_link: bool):
        self.show_propagations = show_propagations
        self.show_link = show_link

    def _format_title(self, wikilink: Wikilink) -> str | None:
        if self.show_link == "Title":
            return wikilink.title
        elif self.show_link == "Wikidata":
            return wikilink.wikidata_id if wikilink.wikidata_id is not None else None
        elif self.show_link == "BabelNet":
            return wikilink.bn_id if wikilink.bn_id is not None else None
        elif self.show_link == "WordNet":
            return wikilink.wn_id if wikilink.wn_id is not None else None
        else:
            raise ValueError

    async def _render(self, page: WikiPage):
        wikilinks_annotation = await page.get_annotation("wikilinks")
        stanza_document = (await page.get_annotation("stanza")).document

        document_tokens = []

        for sentence in stanza_document.sentences:
            sentence_tokens = []
            for token in sentence.tokens:
                sentence_tokens.append(token.text)
            document_tokens.append(sentence_tokens)

        wikilinks_to_apply = []
        for pw in wikilinks_annotation.wikilinks:
            title = self._format_title(pw)
            color = (
                self.get_color(title) if title is not None else self.get_gray_color()
            )
            brightened_color = "#" + brighten_color(color[1:], factor=0.75)
            wikilinks_to_apply.append(
                (
                    pw.sentence_idx,
                    pw.token_span,
                    title if title is not None else "∅",
                    color,
                )
            )
            if self.show_propagations and pw.propagated_spans is not None:
                for ps in pw.propagated_spans:
                    wikilinks_to_apply.append(
                        (
                            ps[0],
                            ps[1],
                            title if title is not None else "∅",
                            brightened_color,
                        )
                    )

        wikilinks_to_apply = sorted(
            wikilinks_to_apply, key=lambda x: (x[0], x[1][0]), reverse=True
        )

        warned_once = False

        for s_idx, (t_start, t_end), label, color in wikilinks_to_apply:
            try:
                text = " ".join(document_tokens[s_idx][t_start:t_end])
            except TypeError:
                # todo this might happen due to overlaps
                if not warned_once:
                    print("overlap found => not all wikiliks will be shown")
                    warned_once = True
                continue
            if t_start + 1 < t_end:
                del document_tokens[s_idx][t_start + 1 : t_end]
            document_tokens[s_idx][t_start] = (text, label, color)

        for sentence_tokens in document_tokens:
            annotated_text(*[_e for t in sentence_tokens for _e in [t, " "]])
            annotated_text()
