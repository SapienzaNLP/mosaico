from . import BodyRenderer, brighten_color
import streamlit as st

from annotated_text import annotated_text

from mosaico.schema import WikiPage


@BodyRenderer.register("srl")
class SRLBodyRenderer(BodyRenderer):
    @staticmethod
    def _render_sidebar_kwargs() -> dict:
        inventory = st.sidebar.radio("Pick one", ["propbank", "verbatlas"])
        return dict(inventory=inventory)

    def __init__(self, inventory: str):
        self.inventory = inventory

    async def _render(self, page: WikiPage):
        try:
            srl_annotation = await page.get_annotation("srl")
        except KeyError:
            st.write('Annotation "wsd" missing. Check out json')
            return

        stanza_document = (await page.get_annotation("stanza")).document

        document_spans = srl_annotation.inventory2document_spans[self.inventory]

        for sentence_idx, sentence in enumerate(stanza_document.sentences):
            if document_spans[sentence_idx] == []:
                st.markdown(
                    f"""<p style="color:lightgray">{sentence.text}</p>""",
                    unsafe_allow_html=True,
                )

            else:
                predicates = []
                for pred_arg_structure in document_spans[sentence_idx]:
                    predicates.append(
                        f"{pred_arg_structure.predicate.token_idx}. {sentence.tokens[pred_arg_structure.predicate.token_idx].text}"
                    )

                selected_predicate = st.selectbox(
                    "Predicate:",
                    options=predicates,
                    help=f"Choose a predicate for the {sentence_idx}-th sentence of article in language {page.language}",
                )

                selected_predicate_idx = predicates.index(selected_predicate)
                selected_pred_arg_structure = document_spans[sentence_idx][
                    selected_predicate_idx
                ]

                color = self.get_color(selected_pred_arg_structure.predicate.label)

                sentence_tokens = []
                for token in sentence.tokens:
                    sentence_tokens.append(token.text)

                labels_to_apply = []
                labels_to_apply.append(
                    (
                        (
                            selected_pred_arg_structure.predicate.token_idx,
                            selected_pred_arg_structure.predicate.token_idx + 1,
                        ),
                        selected_pred_arg_structure.predicate.label,
                        color,
                    )
                )
                for arg in selected_pred_arg_structure.arguments:
                    if arg.role == "V":
                        continue
                    labels_to_apply.append(
                        (
                            (arg.start, arg.end),
                            arg.role,
                            f"#{brighten_color(color[1:], factor=0.5)}",
                        )
                    )

                labels_to_apply = sorted(
                    labels_to_apply, key=lambda x: x[0], reverse=True
                )

                try:
                    for (t_start, t_end), label, color in labels_to_apply:
                        text = " ".join(sentence_tokens[t_start:t_end])
                        title = label
                        if t_start + 1 < t_end:
                            del sentence_tokens[t_start + 1 : t_end]

                        sentence_tokens[t_start] = (text, title, color)

                    annotated_text(*[_e for t in sentence_tokens for _e in [t, " "]])
                    annotated_text()

                except TypeError:
                    sentence_tokens = [token.text for token in sentence.tokens]
                    st.write(" ".join(sentence_tokens))
                    dotted_list = []
                    for (t_start, t_end), label, color in labels_to_apply:
                        dotted_list.append(
                            f"* **{label}**: {t_start} - {t_end} --> *{' '.join(sentence_tokens[t_start: t_end])}*"
                        )
                    st.write("\n".join(dotted_list))

            st.write("---")
