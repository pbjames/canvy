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
    OPENAI_MODEL,
)
from cansync.types import CansyncConfig
from cansync.utils import get_config

logger = logging.getLogger(__name__)


def canvas_files() -> str:
    """
    Produce the local directory of Canvas files so that we can extract text
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
        Retrieve knowledge which will be processed and added to your
        knowledge base.

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
    from agno.models.openai.chat import OpenAIChat
    from agno.tools.duckduckgo import DuckDuckGoTools
    from agno.vectordb.qdrant.qdrant import Qdrant
    from agno.vectordb.search import SearchType

    new_knowledge_queue: list[Document] = []
    agent = Agent(
        model=OpenAIChat(id=OPENAI_MODEL, api_key=config.openai_key),
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
        tools=[DuckDuckGoTools(), canvas_files, create_tool(new_knowledge_queue)],
        add_references=True,
        show_tool_calls=True,
        add_history_to_messages=True,
        num_history_runs=3,
        read_chat_history=True,
        markdown=False,
    )
    while True:
        try:
            user_input = input(">>> ")
            if user_input in ["quit", "/q", "exit"]:
                sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            print("Program exiting...")  # noqa: T201
            sys.exit(0)
        agent.print_response(user_input)  # pyright: ignore[reportUnknownMemberType]
        if new_knowledge_queue and agent.knowledge is not None:
            logger.info("Adding new knowledge")
            agent.knowledge.load_documents(new_knowledge_queue, skip_existing=True)
            new_knowledge_queue.clear()
