#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
    A web crawler for networks’ international calling costs.
"""


from __future__ import print_function

import json
import os
import sys
import time
import textwrap
import argparse
import logging
import coloredlogs

# os.EX_USAGE
# os.EX_NOINPUT
# os.EX_DATAERR
# os.EX_UNAVAILABLE
# os.EX_OSFILE
# os.EX_CANTCREAT

try:
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException
    from selenium.common.exceptions import TimeoutException
    from selenium.common.exceptions import WebDriverException
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
except ImportError as imp_err:
    raise ImportError("Failed to import selenium:\n%s" % imp_err)

__author__ = "Luigi Riefolo"
__version__ = "1.0"
LOAD_DELAY = 10  # seconds
SCRIPT = os.path.basename(__file__)

# Check Python version
if sys.version_info < (2, 6):
    print("%s requires python version >= 2.6." % SCRIPT, file=sys.stderr)
    sys.exit(os.EX_CONFIG)


def get_element(driver, path):
    """ Load for an element to be loaded and return it """
    element = None
    try:
        element_to_load = EC.presence_of_element_located((By.XPATH, path))
        element = WebDriverWait(driver, LOAD_DELAY).until(element_to_load)

    except NoSuchElementException:
        print("Could not find element %s" % path)
    except TimeoutException:
        print("Loading took too much time")

    return element


def is_int(value):
    """ Reports whether the value represents an int"""
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_float(value):
    """ Reports whether the value represents a float"""
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_number(value):
    """ Reports whether the value represents a number"""
    return is_int(value) or is_float(value)


class OperatorWebSite(object):
    """
    Network operator API.
    """

    def __init__(self, driver, data):
        """ """
        self.driver = driver
        self.url = data["url"]
        self.actions = data["actions"]
        self.zones = data["zones"]

    def get_actions(self):
        """ Returns the list of actions. """
        return self.actions

    def get_zones(self):
        """ Returns the list of country zones. """
        return self.zones

    def run_element_method(self, path, method_name, args=None):
        """
        Run a web driver element method.

        It checks whether the element exists and
        runs the requested method with any optional arguments.
        """
        element = get_element(self.driver, path)
        if element is None:
            return False

        ret = False
        attr = self.get_attr(element, method_name)
        # Function attribute
        if hasattr(attr, "__call__"):
            # Function invocation
            if args is not None:
                attr(args)
            else:
                attr()

            ret = True
        # Property attribute
        else:
            print("RET: " + attr)
            ret = attr

        return ret

    def type_zone(self, args):
        """
        Types a zone name into a selected input.

        The input element is selected using the given XPath.
        """
        logging.debug("Executing 'type_zone' action for '%s', input '%s'",
                      args["path"], args["zone"])
        keys = args["zone"] + Keys.RETURN
        return self.run_element_method(args["path"], "send_keys", keys)

    def click(self, args):
        """
        Executes a click action.

        The input element is selected using the given XPath.
        """
        logging.debug("Executing 'click' action for '%s'", args["path"])
        return self.run_element_method(args["path"], "click")

    def get_cost(self, args):
        """
        Returns the calling cost.

        The cost is represented as text within the current element.
        The input element is selected using the given XPath.
        """
        logging.debug("Executing 'get_cost' action for '%s'", args["path"])
        return self.run_element_method(args["path"], "text")

    @staticmethod
    def get_attr(obj, name):
        """
        Return an object attribute.

        It checks whether an attribute exists and returns it.
        Otherwise an AttributeError exception is thrown.
        """
        attr = None
        try:
            attr = getattr(obj, name)
        except AttributeError:
            err_msg = "Class '{} does not contain {}'".format(
                obj.__class__.__name__, name)
            logging.exception(err_msg)
            # raise NotImplementedError(err_msg)

        return attr


def process_actions(zone, operator_data, sleep_time):
    """ Processes all the required actions. """
    res = None

    # Dict containing a list of additional
    # arguments for each available action
    additional_args = {
        "type_zone": {"zone": zone}}

    # Process each action
    for action_data in operator_data.get_actions():
        action_name = action_data.keys()[0]
        path = action_data.values()[0]

        action_args = {"path": path}

        # Add additional action arguments
        if action_name in additional_args:
            key = additional_args[action_name].keys()[0]
            value = additional_args[action_name].values()[0]
            action_args[key] = value

        # Execute the requested web driver action
        method = operator_data.get_attr(operator_data, action_name)

        # Stop processing the current zone
        # if the method execution fails
        res = method(action_args)
        if res is None:
            logging.error("Action '%s' failed, skipping zone '%s'",
                          action_name, zone)
            break

        logging.debug("Sleeping %s seconds ", str(sleep_time))
        time.sleep(sleep_time)

    return res


def process_data(data):
    """ Parse the JSON object containing the data """
    try:
        # Firefox
        driver = webdriver.Chrome()

        # Processe each operator
        for operator in data["operators"]:
            name = operator["name"]
            url = operator["url"]
            logging.info("Operator:\t%s\nURL:\t\t%s", name, url)

            # Visit the URL
            driver.get(url)

            # Create the operator web site object
            operator_data = OperatorWebSite(driver, operator)

            # Process each zone
            logging.info("Country zones:\t")
            for zone in operator_data.get_zones():
                logging.info("\t\t%s:\t", zone)
                cost = process_actions(
                    zone, operator_data, operator["sleep_time"])

                # Check if the result is a number
                if is_number(cost):
                    logging.info("RES: " + cost)
                else:
                    logging.error("Cost does not appear to be a number")

    except WebDriverException:
        driver.quit()
        raise
    finally:
        # Close and quit the browser
        logging.debug("Closing web driver")
        driver.close()


def load_data(file_name):
    ''' Load the data file '''

    parsed_data = None

    # Check whether the file exists
    if not os.path.isfile(file_name):
        logging.error("File '%s' does not exist", file_name)
        sys.exit(os.EX_NOINPUT)

    # Open the file and load its data
    try:
        data_file = open(file_name, 'r')
    except (IOError, OSError) as err:
        raise err
    else:
        try:
            # Load the data file into a JSON object
            parsed_data = json.loads(data_file.read())
        except ValueError as err:
            logging.error("Invalid JSON: %s", err)
    finally:
        data_file.close()

    return parsed_data


def init_log(level, log_file):
    """ Initialise the logging. """
    logger = logging.getLogger(__name__)
    log_format = (
        "[%(asctime)s] [%(levelname)s] "
        "[%(name)s] [%(funcName)s():%(lineno)s] "
        "[PID:%(process)d TID:%(thread)d] %(message)s")

    stream = None
    if log_file is None:
        stream = sys.stdout
    else:
        print("LOG: " + log_file)
        stream = open(log_file, "w+")

    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    log_level = log_levels[level]

    coloredlogs.install(
        level=log_level,
        fmt=log_format,
        isatty=True,
        datefmt="%d/%m/%Y %H:%M:%S",
        stream=stream)

    logger.info("STARTED!!!!!!!!!!!!!!")
    return logger


def get_args():
    """ Get the command-line arguments """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
        description=__doc__)

    # Positional args
    parser.add_argument(
        "data",
        metavar="data",
        type=str,
        help=textwrap.dedent("""\
        File containing the operator URL,
        the list of country zones and the file
        structure for the Selenium driver."""))
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.")
    # Optional args
    parser.add_argument(
        "-l",
        "--log",
        metavar="log",
        type=str,
        help="Write to log file (default STDOUT).")
    parser.add_argument(
        "-i",
        "--log-level",
        metavar="log_level",
        default="info",
        type=str,
        help=("Log levels: debug, info, warning, "
              "error, critical (default info)."))
    parser.add_argument(
        "-o",
        "--out",
        metavar="of",
        type=str,
        help="Write output to file (default STDOUT).")
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Run in quiet mode.")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {0}".format(__version__),
        help="Show version number.")

    return parser.parse_args()


def main():
    """ Main """
    try:
        args = get_args()
        init_log(args.log_level, args.log)
        data = load_data(os.path.realpath(args.data))
        process_data(data)
    # Ctrl-C
    except KeyboardInterrupt, err:
        raise err
    except SystemExit, err:
        raise err
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    return os.EX_OK

if __name__ == '__main__':
    sys.exit(main())
