#!/usr/bin/env python

"""Init script for the APIs."""

import logging


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
