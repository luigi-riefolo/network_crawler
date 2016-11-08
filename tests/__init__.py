"""Unit tests init."""

import json
import os
import time
import unittest

try:
    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException
except ImportError as imp_err:
    raise ImportError('Failed to import \'selenium\':\n' + str(imp_err))

from network_crawler.api.operator_web_site import OperatorWebSite

__all__ = ['json', 'os', 'time', 'unittest',
           'webdriver', 'WebDriverException', 'OperatorWebSite', ]
