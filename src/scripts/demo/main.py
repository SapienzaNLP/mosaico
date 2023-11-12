import argparse
import os
import asyncio
from typing import Coroutine
from beanie import PydanticObjectId
from pydantic import BaseModel, Field

try:
    import streamlit as st
except ModuleNotFoundError:
    print("Package streamlit not installed. Please install it: 'pip install streamlit'")
    exit(1)

try:
    from annotated_text import annotated_text  # noqa
except ModuleNotFoundError:
    print(
        "Package st-annotated-text not installed. Please install it: 'pip install st-annotated-text'"
    )
    exit(1)

from mosaico.schema import init, WikiPage, Language
from src.scripts.demo.renderers import BodyRenderer


def render_sidebar(titles):
    st.sidebar.title("MOSAICo")
    title = st.sidebar.selectbox("Select an article", sorted(titles))
    annotation = st.sidebar.radio("Pick one", BodyRenderer.options())
    body_renderer = BodyRenderer.from_name(
        annotation, **BodyRenderer.render_sidebar_kwargs_from_name(annotation)
    )
    return title, body_renderer


class ProjectedPageModel(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    language: Language
    title: str


async def load_language2page(selected_projected_page: ProjectedPageModel):
    if selected_projected_page.id not in st.session_state:
        selected_page = await WikiPage.get(selected_projected_page.id)
        language2page = {selected_page.language: selected_page}
        async for translated_page in selected_page.list_translations():
            language2page[translated_page.language] = translated_page

        st.session_state[selected_projected_page.id] = language2page

    return st.session_state[selected_projected_page.id]


async def main():
    # init db
    await init(os.environ["MONGO_URI"], "mosaico")

    # set streamlit wide layout
    st.set_page_config(layout="wide")

    # get a bunch of titles and pages
    titles, projected_pages = [], []
    async for projected_page in (
        WikiPage.find().project(ProjectedPageModel).limit(1_000)
    ):
        titles.append(
            f"[{projected_page.language.value.upper()}] {projected_page.title}"
        )
        projected_pages.append(projected_page)

    if len(projected_pages) == 0:
        print("No pages found in DB")
        exit(1)

    # render sidebar
    selected_title, body_renderer = render_sidebar(titles)
    selected_projected_page = projected_pages[titles.index(selected_title)]

    # load from db
    language2page = load_language2page(selected_projected_page)
    if isinstance(language2page, Coroutine):
        language2page = await language2page

    # render

    st.sidebar.markdown("---")
    language = st.sidebar.radio(
        "Languages:",
        [
            selected_projected_page.language.value,
            *[
                l.value
                for l in sorted(language2page, key=lambda x: x.value)
                if l != selected_projected_page.language
            ],
        ],
    )

    await body_renderer.render(language2page[Language(language)])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("conf_path")
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main())
