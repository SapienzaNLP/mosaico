import random
from enum import Enum
from typing import Type

import streamlit as st
from mosaico.schema import WikiPage

colors_md_200 = [
    "#EF9A9A",
    "#F48FB1",
    "#CE93D8",
    "#B39DDB",
    "#9FA8DA",
    "#90CAF9",
    "#81D4fA",
    "#80DEEA",
    "#80CBC4",
    "#A5D6A7",
    "#C5E1A5",
    "#E6EE9C",
    "#FFF590",
    "#FFE082",
    "#FFCC80",
    "#FFAB91",
    "#BCAAA4",
]

color_material_gray = "#EEEEEE"


def color_iterator():
    for c in colors_md_200:
        yield c


def hex_to_rgb(hex_color):
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "%02x%02x%02x" % rgb


def brighten_color(hex_color, factor):
    r, g, b = hex_to_rgb(hex_color)
    r = int(r * (1 - factor) + 255 * factor)
    g = int(g * (1 - factor) + 255 * factor)
    b = int(b * (1 - factor) + 255 * factor)
    return rgb_to_hex((r, g, b))


class BodyRenderer:
    _registry: dict[str, Type["BodyRenderer"]] = {}
    color_it = color_iterator()
    label2color = {}

    @staticmethod
    def options():
        return list(BodyRenderer._registry.keys())

    @staticmethod
    def register(name: str):
        def _register(data_driver: Type["BodyRenderer"]):
            if name in BodyRenderer._registry:
                raise ValueError(f"Renderer {name} already registered")
            BodyRenderer._registry[name] = data_driver
            return data_driver

        return _register

    @staticmethod
    def from_name(name, **kwargs):
        if name not in BodyRenderer._registry:
            raise ValueError(
                f"{name} is not a registered BodyRenderer. "
                f"Supported BodyRenderer-s are: {list(BodyRenderer._registry.keys())}"
            )
        return BodyRenderer._registry[name](**kwargs)

    @staticmethod
    def render_sidebar_kwargs_from_name(name):
        if name not in BodyRenderer._registry:
            raise ValueError(
                f"{name} is not a registered BodyRenderer. "
                f"Supported BodyRenderer-s are: {list(BodyRenderer._registry.keys())}"
            )
        return BodyRenderer._registry[name]._render_sidebar_kwargs()

    @staticmethod
    def _render_sidebar_kwargs() -> dict:
        return {}

    @classmethod
    def get_color(cls, label):
        if label not in BodyRenderer.label2color:
            try:
                BodyRenderer.label2color[label] = next(BodyRenderer.color_it)
            except StopIteration:
                BodyRenderer.label2color[label] = "#%06x" % random.randint(
                    0x969696, 0xFFFFFF
                )

        return BodyRenderer.label2color[label]

    @classmethod
    def get_gray_color(cls):
        return color_material_gray

    async def render(self, page: WikiPage):
        st.write(f"# [{page.title}]({page.link})")
        await self._render(page)

    async def _render(self, page: WikiPage):
        raise NotImplementedError


from .wikimedia import BodyRenderer, CirrusBodyRenderer, WikipageBodyRenderer  # noqa
from .raw import RawJSONBodyRenderer  # noqa
from .stanza_views import StanzaBodyRenderer, StanzaNERBodyRenderer  # noqa
from .wsd import WSDBodyRenderer  # noqa
from .srl import SRLBodyRenderer  # noqa
from .rel_ex import REBodyRenderer  # noqa
from .amr import AMRBodyRenderer  # noqa
