import os
from pathlib import Path

from agno.document.base import Document
from agno.document.reader.pdf_reader import PDFReader
from mcp.server import FastMCP

from cansync.utils import get_config

mcp = FastMCP()


@mcp.tool()
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

    return mcp.tool()(retrieve_knowledge)
