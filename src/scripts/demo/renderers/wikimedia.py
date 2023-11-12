from . import BodyRenderer, brighten_color
import streamlit as st

from annotated_text import annotated_text

from mosaico.schema import WikiPage


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
    async def _render(self, page: WikiPage):
        # write categories
        st.subheader("Categories")
        categories = (await page.get_annotation("cirrus")).data["category"]
        cols = st.columns(3)
        for i in range(len(categories)):
            with cols[i % 3]:
                st.markdown(f"* {categories[i]}")
        st.markdown("---")
        # write text
        st.subheader(page.title)
        st.write(page.text)


@BodyRenderer.register("section")
class SectionBodyRenderer(BodyRenderer):
    async def _render(self, page: WikiPage):
        sentence2section = {}

        sectioning_annotation = await page.get_annotation("sectioning")
        stanza_document = (await page.get_annotation("stanza")).document

        for section in sectioning_annotation.sections:
            for idx in range(section.sentences_span[0], section.sentences_span[1]):
                sentence2section[idx] = section.name

        last_section = None
        for idx, sentence in enumerate(stanza_document.sentences):
            section = sentence2section.get(idx, None)
            if section is None:
                st.markdown(
                    f"""<p style="color:lightgray">{sentence.text}</p>""",
                    unsafe_allow_html=True,
                )
            else:
                if section != last_section:
                    st.write(f"## {section}")
                    last_section = section
                st.write(sentence.text)


@BodyRenderer.register("wikilinks")
class WikilinkBodyRenderer(BodyRenderer):
    @staticmethod
    def _render_sidebar_kwargs() -> dict:
        show_propagations = st.sidebar.checkbox("Show propagations")
        return dict(show_propagations=show_propagations)

    def __init__(self, show_propagations: bool):
        self.show_propagations = show_propagations

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
        for pw in wikilinks_annotation.projected_wikilinks:
            title = pw.title
            color = self.get_color(pw.title)
            brightened_color = "#" + brighten_color(color[1:], factor=0.75)
            wikilinks_to_apply.append((pw.sentence_idx, pw.token_span, pw.title, color))
            if self.show_propagations and pw.propagated_spans is not None:
                for ps in pw.propagated_spans:
                    wikilinks_to_apply.append((ps[0], ps[1], title, brightened_color))

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
