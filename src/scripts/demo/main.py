import asyncio
import os
from typing import Coroutine

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

try:
    import streamlit as st
except ModuleNotFoundError:
    print("Package streamlit not installed. Please install it: 'pdm install -G demo'")
    exit(1)

try:
    from annotated_text import annotated_text  # noqa
except ModuleNotFoundError:
    print(
        "Package st-annotated-text not installed. Please install it: 'pdm install -G demo'"
    )
    exit(1)

from mosaico.schema import (
    Language,
    ProjectedWikiPageModel_LanguageTitleType,
    WikiPage,
    init,
)

from src.scripts.demo.renderers import BodyRenderer


def render_sidebar(titles):
    st.sidebar.title("MOSAICo")
    selectbox_title = st.sidebar.selectbox("Choose from a random list", sorted(titles))
    textinput_title = st.sidebar.text_input(
        "Or enter title manually", placeholder="[EN] Barack Obama"
    )
    title = textinput_title if textinput_title != "" else selectbox_title
    annotation = st.sidebar.radio("Pick one", BodyRenderer.options())
    body_renderer = BodyRenderer.from_name(
        annotation, **BodyRenderer.render_sidebar_kwargs_from_name(annotation)
    )
    return title, body_renderer


async def load_language2page(language: Language, title: str):
    if (language, title) not in st.session_state:
        selected_page = await WikiPage.find_one(
            WikiPage.language == language, WikiPage.title == title
        )
        language2page = {selected_page.language: selected_page}
        async for translated_page in selected_page.list_translations():
            language2page[translated_page.language] = translated_page

        st.session_state[language, title] = language2page

    return st.session_state[language, title]


async def main():
    # init db
    mongo_uri = os.environ.get("MONGO_URI", None)
    if mongo_uri is None:
        raise ValueError("no MONGO_URI env variable found, did you forget to set it?")

    await init(mongo_uri, "mosaico")

    # set streamlit wide layout
    st.set_page_config(layout="wide")

    # get a bunch of titles and pages
    titles = []
    async for projected_page in (
        WikiPage.find(
            {
                "is_mosaico_core": True,
            }
        )
        .project(ProjectedWikiPageModel_LanguageTitleType)
        .limit(1_000)
    ):
        titles.append(
            f"[{projected_page.language.value.upper()}] {projected_page.title}"
        )

    if len(titles) == 0:
        print("No pages found in DB")
        exit(1)

    # render sidebar
    selected_title, body_renderer = render_sidebar(titles)
    language, title = Language(selected_title[1:3].lower()), selected_title[5:]

    # load from db
    language2page = load_language2page(language, title)
    if isinstance(language2page, Coroutine):
        language2page = await language2page

    # render

    st.sidebar.markdown("---")
    language = st.sidebar.radio(
        "Languages:",
        [
            language.value,
            *[
                l.value
                for l in sorted(language2page, key=lambda x: x.value)
                if l != language
            ],
        ],
    )

    await body_renderer.render(language2page[Language(language)])


if __name__ == "__main__":
    asyncio.run(main())
