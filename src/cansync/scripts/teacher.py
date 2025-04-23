import logging
import os
import sys
from pathlib import Path

from agno.document.base import Document
from agno.document.reader.pdf_reader import PDFReader

from cansync.const import (
    AGENT_DESCRIPTION,
    AGENT_INSTRUCTIONS,
    OPENAI_EMBEDDINGS,
    PROBLEM_SHEET_1,
    STOP_WORDS,
)
from cansync.types import CansyncConfig
from cansync.utils import create_dir, get_config, provider

logger = logging.getLogger(__name__)


def validate_typst(content: str) -> tuple[bool, str]:
    v = True, ""
    return v


def make_problem_sheet(file_name: str, content: str) -> str:
    """
    Produce a problem sheet for the user by recycling content from relevant slides
    and prior knowledge to make enganging yet conformant problems for revision.

    Args:
        file_name: File name ending in .pdf which denotes which topic the sheet is about
        content: Body of the sheet which is written in vanilla typst (important) language

    Return:
        Result
    """
    import typst

    res, err = validate_typst(content)
    if not res:
        return err

    config = get_config()
    sheets_dir = config.storage_path / "Problem Sheets"
    create_dir(sheets_dir)
    content = f"""
{PROBLEM_SHEET_1.format("class", "student", "title")}
{content}
    """
    out = typst.compile(content.encode("utf-8"))
    with open(sheets_dir / file_name, "wb") as fp:
        fp.write(out)
    return "Done"


def canvas_files() -> str:
    """
    Produce the local directory of Canvas files / slides so that we can extract text
    from the appropriate files

    Returns:
        Dictionary of {file names -> relative paths}
    """
    config = get_config()
    return str(
        {
            fn: Path(dor).relative_to(config.storage_path) / fn
            for dor, _, fns in os.walk(config.storage_path)
            for fn in fns
        }
    )


def create_tool(queue: list[Document]):
    def retrieve_knowledge(pdf_rel_path: Path):
        """
        Retrieve knowledge which will be processed and added to your knowledge base.

        Args:
            pdf_rel_path: Relative path given by other tools pointing to a PDF file
            queue:

        Returns:
            Confirmation
        """
        config = get_config()
        queue.extend(PDFReader().read(config.storage_path / pdf_rel_path))
        return "Done. You will now receive knowledge from god."

    return retrieve_knowledge


def teacher(config: CansyncConfig) -> None:
    """
    Basically talk to chatgpt but it can discover about everything in the files downloaded
    through the download tool
    """
    if config.openai_key is None:
        logger.error("There's no OpenAI key")
        sys.exit(1)
    from agno.agent.agent import Agent
    from agno.embedder.openai import OpenAIEmbedder
    from agno.knowledge.pdf import PDFKnowledgeBase
    from agno.tools.duckduckgo import DuckDuckGoTools
    from agno.vectordb.qdrant.qdrant import Qdrant
    from agno.vectordb.search import SearchType

    new_knowledge_queue: list[Document] = []
    agent = Agent(
        model=provider(config),
        description=AGENT_DESCRIPTION,
        instructions=AGENT_INSTRUCTIONS,
        knowledge=PDFKnowledgeBase(
            path=config.storage_path,
            vector_db=Qdrant(
                collection="canvas-files",
                path=str(config.storage_path / ".vector_db"),
                search_type=SearchType.hybrid,
                embedder=OpenAIEmbedder(
                    id=OPENAI_EMBEDDINGS, api_key=config.openai_key
                ),
            ),
        ),
        tools=[
            DuckDuckGoTools(),
            canvas_files,
            create_tool(new_knowledge_queue),
            make_problem_sheet,
        ],
        show_tool_calls=True,
        add_history_to_messages=True,
        num_history_runs=3,
        read_chat_history=True,
        markdown=True,
    )
    while True:
        user_input = input(">>> ")
        if user_input in STOP_WORDS:
            sys.exit(0)
        agent.print_response(user_input)  # pyright: ignore[reportUnknownMemberType]
        if new_knowledge_queue and agent.knowledge is not None:
            logger.info("Adding new knowledge")
            agent.knowledge.load_documents(new_knowledge_queue, skip_existing=True)
            new_knowledge_queue.clear()
