#!/usr/bin/env python

"""Init script for the APIs."""

import logging
import network_crawler
from network_crawler.api.operator_web_site import OperatorWebSite

__all__ = [OperatorWebSite, ]
__author__ = network_crawler.__author__
__version__ = network_crawler.__version__


try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        """
        Set default logging handler.

        It avoids "No handler found" warnings.
        """

        def emit(self, record):
            """Emit stub."""
            pass

logging.getLogger(__name__).addHandler(logging.NullHandler())
