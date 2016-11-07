#!/usr/bin/env python

"""Init script for the APIs."""

import logging
from api.operator_web_site import OperatorWebSite

__all__ = ["OperatorWebSite"]
__author__ = "Luigi Riefolo"
__version__ = "1.0.0"

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        """
        Set default logging handler.

        It avoids "No handler found" warnings.
        """
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(logging.NullHandler())
