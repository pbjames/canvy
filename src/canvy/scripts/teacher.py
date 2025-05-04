import logging
import os
import sys
from pathlib import Path

import typst
from agno.document.base import Document
from agno.document.reader.pdf_reader import PDFReader

from canvy.const import (
    AGENT_DESCRIPTION,
    AGENT_INSTRUCTIONS,
    OPENAI_EMBEDDINGS,
    PROBLEM_SHEET_1,
    PS_DIRNAME,
    STOP_WORDS,
)
from canvy.types import CanvyConfig
from canvy.utils import create_dir, provider

logger = logging.getLogger(__name__)


def validate_typst(content: str) -> tuple[bool, bytes]:
    """
    Tell the LLM off for generating non-compiling typst code

    Args:
        content: Text to evaluate and compile into PDF

    Returns:
        (True, content): Conversion successful
        (False, err_msg): Conversion fails
    """
    try:
        logger.info(f"content: {content}")
        converted = typst.compile(content.encode("utf-8"))
        return (True, converted)
    except Exception as e:
        logger.warning(f"Shit doesn't compile: {e}")
        return (False, str(e).encode("utf-8"))


def make_problem_sheet(config: CanvyConfig):
    def make_problem_sheet(
        file_name: str, class_name: str, title: str, content: str
    ) -> str:
        """
        Produce a problem sheet for the user by recycling content from relevant slides
        and prior knowledge to make engaging yet conformant problems for revision. Focus
        heavily on what the user is asking for.

        Args:
            file_name: File name ending in .pdf
            class_name: Name of the current module or class the topic falls under
            title: Title of the problem sheet
            content: Body of the problem sheet - use normal markdown with many headings

        Return:
            Result
        """
        res, body = validate_typst(
            f"""r
    {PROBLEM_SHEET_1.format(class_name=class_name, student="Mike Hockurts", title=title)}
    {content.replace("#", "=")}
        """
        )
        if not res:
            return body.decode("utf-8")
        sheets_dir = config.storage_path / PS_DIRNAME
        create_dir(sheets_dir)
        with open(sheets_dir / file_name, "wb") as fp:
            fp.write(body)
        logger.info("File written successfully")
        return "Done"

    return make_problem_sheet


def canvas_files(config: CanvyConfig):
    def canvas_files() -> str:
        """
        Produce the local directory of Canvas files / slides so that we can extract text
        from the appropriate files

        Returns:
            Dictionary of {file names -> relative paths}
        """
        return str(
            {
                fn: Path(dir).relative_to(config.storage_path) / fn
                for dir, _, fns in os.walk(config.storage_path)
                for fn in fns
            }
        )

    return canvas_files


def retrieve_knowledge(config: CanvyConfig, queue: list[Document]):
    def retrieve_knowledge(pdf_rel_path: Path):
        """
        Retrieve knowledge which will be processed and added to your knowledge base.

        Args:
            pdf_rel_path: Relative path given by other tools pointing to a PDF file
            queue:

        Returns:
            Confirmation
        """
        queue.extend(PDFReader().read(config.storage_path / pdf_rel_path))
        return "Done. You will now receive knowledge from god."

    return retrieve_knowledge


def teacher(config: CanvyConfig, prior_knowledge: list[Document] | None = None) -> None:
    """
    Use LLMs to ask questions about the content of the slides from Canvas, the resources
    MUST be downloaded locally beforehand.

    Args:
        prior_knowledge: Documents to add prior to interaction
    """
    from agno.agent.agent import Agent
    from agno.embedder.openai import OpenAIEmbedder
    from agno.knowledge.pdf import PDFKnowledgeBase
    from agno.tools.duckduckgo import DuckDuckGoTools
    from agno.vectordb.qdrant.qdrant import Qdrant
    from agno.vectordb.search import SearchType

    new_knowledge_queue: list[Document] = prior_knowledge or []
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
            canvas_files(config),
            retrieve_knowledge(config, new_knowledge_queue),
            make_problem_sheet(config),
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
