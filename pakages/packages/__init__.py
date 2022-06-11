from .python import PythonPackage
from pakages.logger import logger
import os


def get_package(root):
    """
    Get a packager based on a context
    """
    if os.path.exists(root):
        if PythonPackage.matches(root):
            return PythonPackage(root)
    logger.exit(f"We currently don't support a builder for content in {root}")
