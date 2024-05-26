from beanie import init_beanie as _init_beanie
from motor.motor_asyncio import AsyncIOMotorClient as _AsyncIOMotorClient

from .annotations import (
    AMRAnnotation,  # noqa
    AMRGraph,  # noqa
    Annotation,  # noqa
    CirrusAnnotation,  # noqa
    LinkedAnnotationContainer,  # noqa
    MaterializedAnnotationContainer,  # noqa
    MissedWikilink,  # noqa
    Paragraph,  # noqa
    PredArgStructure,  # noqa
    ProjectedWikilink,  # noqa
    REAnnotation,  # noqa
    RETriple,  # noqa
    Section,  # noqa
    SectioningAnnotation,  # noqa
    SRLAnnotation,  # noqa
    StanzaAnnotation,  # noqa
    StanzaAnnotationDocument,  # noqa
    StanzaAnnotationSentence,  # noqa
    StanzaAnnotationToken,  # noqa
    StanzaAnnotationWord,  # noqa
    Wikilink,  # noqa
    WikilinksAnnotation,  # noqa
    WSDAnnotation,  # noqa
    WSDSpanAnnotation,  # noqa
)
from .interlanguage_link import InterlanguageLink, Language  # noqa
from .wikipage import ProjectedWikiPageModel_LanguageTitleType, WikiPage  # noqa


async def init(mongo_uri, db, write_user: bool = False):
    # Create Motor client
    client = _AsyncIOMotorClient(mongo_uri)

    if not write_user:
        # todo open issue on beanie and fix this write_user nonsense
        print("careful, beanie issue still open")
        LinkedAnnotationContainer.Settings.indexes = []
        InterlanguageLink.Settings.indexes = []
        WikiPage.Settings.indexes = []

    # Initialize beanie with the Sample document class and a database
    await _init_beanie(
        database=client[db],
        document_models=[LinkedAnnotationContainer, InterlanguageLink, WikiPage],
    )
