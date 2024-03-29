import os

from pakages.logger import logger

from .python import PythonPackage


def get_package(root):
    """
    Get a packager based on a context
    """
    if isinstance(root, list):
        root = root[0]
    if os.path.exists(root):
        if PythonPackage.matches(root):
            return PythonPackage(root)
    logger.exit(f"We currently don't support a builder for content in {root}")
