import os
from pathlib import Path

from mcp.server import FastMCP

from cansync.utils import get_config

mcp = FastMCP()


@mcp.tool()
def canvas_files() -> dict[str, Path]:
    """
    Retrieve the local directory of Canvas files so that we can extract text
    from the appropriate files

    Returns:
        Dictionary of {file names -> relative paths}
    """
    config = get_config()
    return {
        fn: Path(dor).relative_to(config.storage_path) / fn
        for dor, _, fns in os.walk(config.storage_path)
        for fn in fns
    }
