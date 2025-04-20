import logging
import sys
from getpass import getpass
from pathlib import Path

from canvasapi.canvas import Canvas, Course
from typer import Typer

from cansync.const import (
    AGENT_DESCRIPTION,
    AGENT_INSTRUCTIONS,
    DEFAULT_DOWNLOAD_DIR,
    OPENAI_MODEL,
)
from cansync.scripts.downloader import download as _download
from cansync.scripts.teacher import canvas_files, create_tool
from cansync.types import CansyncConfig
from cansync.utils import (
    get_config,
    setup_logging,
)
from cansync.utils import set_config as utils_set_config

cli = Typer()
logger = logging.getLogger(__name__)


def default_config():
    config = get_config()
    canvas = Canvas(config.canvas_url, config.canvas_key)
    return canvas, config


@cli.command()
def download(force: bool = False):
    canvas, config = default_config()
    _download(canvas, config.canvas_url, force=force)


@cli.command()
def teacher():
    _, config = default_config()
    if config.openai_key is None:
        logger.error("There's no OpenAI key")
        sys.exit(1)
    from agno.agent.agent import Agent
    from agno.embedder.openai import OpenAIEmbedder
    from agno.knowledge.pdf import PDFKnowledgeBase
    from agno.models.openai.chat import OpenAIChat
    from agno.tools.duckduckgo import DuckDuckGoTools
    from agno.vectordb.qdrant.qdrant import Qdrant
    from agno.vectordb.search import SearchType

    new_knowledge_queue = []
    agent = Agent(
        model=OpenAIChat(id=OPENAI_MODEL, api_key=config.openai_key),
        description=AGENT_DESCRIPTION,
        instructions=AGENT_INSTRUCTIONS,
        knowledge=PDFKnowledgeBase(
            path=config.storage_path,
            vector_db=Qdrant(
                collection="canvas-files",
                path="tmp/qdrant",
                search_type=SearchType.hybrid,
                embedder=OpenAIEmbedder(
                    id="text-embedding-3-small", api_key=config.openai_key
                ),
            ),
        ),
        tools=[DuckDuckGoTools(), canvas_files, create_tool(new_knowledge_queue)],
        # add_references=True,
        show_tool_calls=True,
        add_history_to_messages=True,
        num_history_runs=3,
        read_chat_history=True,
        markdown=False,
    )
    # INFO: Might be bad to keep this
    # if agent.knowledge is not None:
    #     agent.knowledge.load()
    while True:
        agent.print_response(input(">>> "))
        if new_knowledge_queue and agent.knowledge is not None:
            logger.info("Adding new knowledge information")
            agent.knowledge.load_documents(new_knowledge_queue)
            new_knowledge_queue.clear()


@cli.command()
def courses():
    canvas, _ = default_config()
    courses: list[Course] = list(canvas.get_courses(enrollment_state="active"))
    for course in courses:
        print(f"{course}")  # noqa: T201


@cli.command()
def set_config(
    canvas_url: str, storage_path: Path | None = None, openai_key: str | None = None
):
    canvas_key = getpass("Canvas API Key: ")
    config = CansyncConfig(
        canvas_url=canvas_url,
        canvas_key=canvas_key,
        storage_path=storage_path or DEFAULT_DOWNLOAD_DIR,
        openai_key=openai_key,
    )
    utils_set_config(config)


def main():
    setup_logging()
    cli()


if __name__ == "__main__":
    main()
