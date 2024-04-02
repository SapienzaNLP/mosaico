from typing import ClassVar, Optional

from pydantic import BaseModel, model_validator

from ..wikipage import WikiPage
from .base import Annotation

_pos2score = {
    "ADJ": 1,
    "ADP": 0,
    "ADV": 1,
    "CCONJ": 0,
    "DET": 0,
    "INTJ": 0,
    "NOUN": 3,
    "NUM": 0,
    "PART": 0,
    "PRON": 0,
    "PUNCT": 0,
    "SCONJ": 0,
    "SYM": 0,
    "VERB": 2,
    "X": 1,
}


def multipos_to_pos(pos_s: list[str]) -> str:
    transformations = {"AUX": "VERB", "PROPN": "NOUN"}
    pos_s = [transformations.get(pos, pos) for pos in pos_s]
    if len(pos_s) == 1 or len(set(pos_s)) == 1:
        return pos_s[0]
    else:
        if "NOUN" in pos_s:
            return "NOUN"
        elif "VERB" in pos_s:
            return "VERB"
        else:
            return max(pos_s, key=lambda x: _pos2score[x])


_pos_classes = [
    "ADJ",
    "ADP",
    "ADV",
    "AUX",
    "CCONJ",
    "DET",
    "INTJ",
    "NOUN",
    "NUM",
    "PART",
    "PRON",
    "PROPN",
    "PUNCT",
    "SCONJ",
    "SYM",
    "VERB",
    "X",
]
_pos2idx = {p: i for i, p in enumerate(_pos_classes)}
_idx2pos = {i: p for i, p in enumerate(_pos_classes)}

_morph_classes = [
    "\u2205",
    "Number=Sing",
    "Gender=Masc",
    "Gender=Fem",
    "Number=Plur",
    "PronType=Art",
    "Definite=Def",
    "Person=3",
    "VerbForm=Fin",
    "Mood=Ind",
    "Case=Nom",
    "NumType=Card",
    "Tense=Past",
    "Tense=Pres",
    "Case=Dat",
    "VerbForm=Part",
    "Gender=Neut",
    "PronType=Prs",
    "Case=Acc",
    "Definite=Ind",
    "Degree=Pos",
    "NumForm=Digit",
    "Foreign=Yes",
    "PunctType=Comm",
    "Case=Gen",
    "VerbForm=Inf",
    "PunctType=Peri",
    "PunctType=Brck",
    "PronType=Dem",
    "PronType=Rel",
    "Poss=Yes",
    "Voice=Pass",
    "PronType=Ind",
    "VerbForm=Ger",
    "Reflex=Yes",
    "PrepCase=Npr",
    "PunctType=Quot",
    "PunctSide=Fin",
    "PunctSide=Ini",
    "Tense=Imp",
    "PronType=Int,Rel",
    "NumType=Ord",
    "Polarity=Neg",
    "AdvType=Tim",
    "PunctType=Colo",
    "Degree=Cmp",
    "Clitic=Yes",
    "Number[psor]=Sing",
    "Mood=Sub",
    "Person=1",
    "Person[psor]=3",
    "PronType=Neg",
    "Person=2",
    "PronType=Tot",
    "PunctType=Semi",
    "PronType=Int",
    "Gender[psor]=Masc,Neut",
    "Tense=Fut",
    "Mood=Cnd",
    "Number[psor]=Plur",
    "Degree=Sup",
    "PunctType=Dash",
    "Mood=Imp",
    "Case=Acc,Nom",
    "NumType=Frac",
    "Person[psor]=2",
    "Abbr=Yes",
    "PunctType=Qest",
    "NumForm=Word",
    "Person[psor]=1",
    "PunctType=Excl",
    "Degree=Abs",
    "ExtPos=ADP",
    "PrepCase=Pre",
    "NumType=Mult",
    "NumForm=Roman",
    "PronType=Emp",
    "Typo=Yes",
    "Polarity=Pos",
    "PronType=Exc",
    "Polite=Form",
    "Case=Com",
    "ExtPos=ADV",
    "Verbform=Fin",
    "Style=Slng",
    "Verbform=Inf",
]
_morph_compression = {c: i for i, c in enumerate(_morph_classes)}
_morph_decompression = {i: c for i, c in enumerate(_morph_classes)}


class StanzaAnnotationWord(BaseModel):
    d: tuple[str, int, list[str | int]]  # text, pos_, morph_
    l: Optional[str] = None

    _text: Optional[str] = None

    @property
    def text(self) -> str:
        return self._text

    _pos: Optional[str] = None

    @property
    def pos(self) -> str:
        return self._pos

    _morph: Optional[str] = None

    @property
    def morph(self) -> str:
        return self._morph

    _lemma: Optional[str] = None

    @property
    def lemma(self) -> str:
        return self._lemma

    @model_validator(mode="before")
    def handle_compression(cls, data: dict) -> dict:
        if "d" not in data:
            assert "text" in data
            data["d"] = (
                data["text"],
                _pos2idx[data["pos"]],
                [
                    _morph_compression.get(feat, feat)
                    for feat in data["morph"].split("|")
                ],
            )
            data["l"] = data["lemma"] if data["lemma"] != data["text"] else None

        return data

    async def prepare_with_page(self, page: WikiPage):
        self._text = self.d[0]
        self._pos = _idx2pos[self.d[1]]
        self._morph = "|".join(
            [
                _morph_decompression[feat] if isinstance(feat, int) else feat
                for feat in self.d[2]
            ]
        )

        self._lemma = self.l


class StanzaAnnotationToken(BaseModel):
    d: tuple[tuple[int, int], int, list[list[str | int]]]  # char span, pos_, morph_
    e: Optional[dict] = None  # extras
    w: Optional[list[StanzaAnnotationWord]] = None  # words
    c: Optional[tuple[int, int]] = (
        None  # char mapping relative to cleaned source text in cirrus annotation
    )

    @property
    def char_start(self) -> int:
        return self.d[0][0]

    @property
    def char_end(self) -> int:
        return self.d[0][1]

    _text: Optional[str] = None

    @property
    def text(self) -> str:
        return self._text

    _pos: Optional[str] = None

    @property
    def pos(self) -> str:
        return self._pos

    _morph: Optional[str] = None

    @property
    def morph(self) -> str:
        return self._morph

    _lemma: Optional[str] = None

    @property
    def lemma(self) -> str:
        return self._lemma

    _ner: Optional[str] = None

    @property
    def ner(self) -> str:
        return self._ner

    @property
    def words(self) -> Optional[list[StanzaAnnotationWord]]:
        return self.w

    @property
    def cleaned_source_text_char_offset(self) -> Optional[tuple[int, int]]:
        return self.c

    @model_validator(mode="before")
    def handle_compression(cls, data: dict) -> dict:
        if "d" not in data:
            assert "char_start" in data

            extras = dict()
            if data["lemma"] != data["text"]:
                extras["l"] = data["lemma"]
            if data["ner"] != "O":
                extras["n"] = data["ner"]

            data["d"] = (
                (data["char_start"], data["char_end"]),
                _pos2idx[data["pos"]],
                [
                    [
                        _morph_compression.get(feat, feat)
                        for feat in word_morphological_features.split("|")
                    ]
                    for word_morphological_features in data["morph"].split("___")
                ],
            )
            data["e"] = extras if len(extras) > 0 else None
            data["w"] = data.get("words", None)
            data["c"] = data.get("cleaned_source_text_char_offset", None)

        return data

    async def prepare_with_page(self, page: WikiPage):
        self._char_start, self._char_end = self.d[0]
        self._pos = _idx2pos[self.d[1]]
        self._morph = "___".join(
            [
                "|".join(
                    [
                        _morph_decompression[feat] if isinstance(feat, int) else feat
                        for feat in word_morphological_features
                    ]
                )
                for word_morphological_features in self.d[2]
            ]
        )

        self._text = page.text[self.char_start : self.char_end]
        self._lemma = self.e.get("l", self.text) if self.e is not None else self.text
        self._ner = self.e.get("n", "O") if self.e is not None else "O"

        if self.w is not None:
            for word in self.w:
                await word.prepare_with_page(page)


class StanzaAnnotationSentence(BaseModel):
    t: list[StanzaAnnotationToken]
    _text: Optional[str] = None

    @property
    def char_start(self) -> int:
        return self.tokens[0].char_start

    @property
    def char_end(self) -> int:
        return self.tokens[-1].char_end

    @property
    def text(self) -> str:
        return self._text

    @property
    def tokens(self) -> list[StanzaAnnotationToken]:
        return self.t

    @model_validator(mode="before")
    def handle_compression(cls, data: dict) -> dict:
        if "t" not in data:
            assert "tokens" in data
            data["t"] = data["tokens"]
        return data

    async def prepare_with_page(self, page: WikiPage):
        for token in self.tokens:
            await token.prepare_with_page(page)

        self._text = page.text[self.char_start : self.char_end]


class StanzaAnnotationDocument(BaseModel):
    sentences: list[StanzaAnnotationSentence]
    _text: Optional[str] = None

    @property
    def char_start(self) -> int:
        return self.sentences[0].char_start

    @property
    def char_end(self) -> int:
        return self.sentences[-1].char_end

    @property
    def text(self) -> str:
        return self._text

    async def _prepare_with_page(self, page: WikiPage):
        for sentence in self.sentences:
            await sentence.prepare_with_page(page)

        self._text = page.text[self.char_start : self.char_end]


class StanzaAnnotation(Annotation):
    """
    A StanzaAnnotation object over a page gets gigantic very quickly, even to the point where some docs
    might crash due to exceeding the max record size allowed in mongo (16MB).

    This code, albeit somewhat complicated and apparently redundant (the stuff with Python properties), is meant
    to reduce the record size by avoiding duplicating any kind of redudant information.
    """

    name: ClassVar[str] = "stanza"
    document: StanzaAnnotationDocument

    async def _prepare_with_page(self, page: WikiPage):
        await self.document._prepare_with_page(page)
