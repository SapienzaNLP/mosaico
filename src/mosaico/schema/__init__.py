from motor.motor_asyncio import AsyncIOMotorClient as _AsyncIOMotorClient
from beanie import init_beanie as _init_beanie
from .annotations import (
    Annotation,  # noqa
    MaterializedAnnotationContainer,  # noqa
    LinkedAnnotationContainer,  # noqa
    CirrusAnnotation,  # noqa
    StanzaAnnotation,  # noqa
    StanzaAnnotationDocument,  # noqa
    StanzaAnnotationSentence,  # noqa
    StanzaAnnotationToken,  # noqa
    StanzaAnnotationWord,  # noqa
    SectioningAnnotation,  # noqa
    Section,  # noqa
    WikilinksAnnotation,  # noqa
    MissedWikilink,  # noqa
    ProjectedWikilink,  # noqa
    WSDAnnotation,  # noqa
    WSDSpanAnnotation,  # noqa
    SRLAnnotation,  # noqa
    PredArgStructure,  # noqa
)
from .interlanguage_link import InterlanguageLink, Language  # noqa
from .wikipage import WikiPage  # noqa


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
