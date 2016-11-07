#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
A web crawler for networks’ international calling costs.
"""


from __future__ import print_function

import json
import os
import re
import sys
import time
import textwrap
import argparse
import logging
import coloredlogs


try:
    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException
except ImportError as imp_err:
    raise ImportError('Failed to import \'selenium\':\n' + imp_err)

from network_crawler.api.operator_web_site import OperatorWebSite
from __init__ import __version__


SCRIPT = os.path.basename(__file__)
LOG_FILE = SCRIPT + '.log'
script_args = None

# Check Python version
if sys.version_info < (2, 6):
    print('%s requires python version >= 2.6' % SCRIPT, file=sys.stderr)
    sys.exit(os.EX_CONFIG)


def is_int(value):
    """ Reports whether the value represents an int. """
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_float(value):
    """ Reports whether the value represents a float. """
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_number(value):
    """ Reports whether the value represents a number. """
    return is_int(value) or is_float(value)


def process_actions(zone, operator_obj, sleep_time):
    """ Processes all the required actions. """
    res = None

    # Dict containing a list of additional
    # arguments for each available action
    additional_args = {
        'type_zone': {'zone': zone}}

    # Process each action
    for action_data in operator_obj.get_actions():
        action_name = action_data.keys()[0]
        path = action_data.values()[0]

        action_args = {'path': path}

        # Add additional action arguments
        if action_name in additional_args:
            key = additional_args[action_name].keys()[0]
            value = additional_args[action_name].values()[0]
            action_args[key] = value

        # Execute the requested web driver action
        method = operator_obj.get_attr(operator_obj, action_name)

        # Stop processing the current zone
        # if the method execution fails
        res = method(action_args)
        if res is None:
            logging.error('Action \'%s\' failed, skipping zone \'%s\'',
                          action_name, zone)
            break

        logging.debug('Sleeping %s seconds ', str(sleep_time))
        time.sleep(sleep_time)

    return res


def log(msg, not_new_line=None):
    """ Logging function. """

    # Do not log in quiet mode or if
    # a JSON document is required
    if script_args.quiet or script_args.json:
        return

    # Print to STDOUT
    if script_args.out is None:
        if not_new_line:
            print(msg, end='')
        else:
            print(msg)
    # Print to file
    else:
        if not_new_line:
            print(msg, file=script_args.out, end='')
        else:
            print(msg + os.linesep, file=script_args.out)


def process_data(data):
    """ Parse the JSON object containing the data. """
    try:
        # Chrome driver
        driver = webdriver.Chrome()

        # Process each operator
        for operator in data['operators']:
            name = operator['name']
            url = operator['url']

            logging.info('Operator: %s', name)
            logging.info('URL: %s', url)
            log('Operator:\t%s\nURL:\t\t%s' % (name, url))

            # Visit the URL
            driver.get(url)

            # Create the operator web site object
            operator_obj = OperatorWebSite(driver, operator)

            # Dict containing the list of zones
            # with their respective costs
            costs = dict()

            # Process each zone
            log('Country zones:\t')
            for zone in operator_obj.get_zones():
                logging.info('Zone: %s\t', zone)
                log('\t\t{}'.format(zone).ljust(30), not_new_line=True)

                cost = process_actions(
                    zone, operator_obj, operator['sleep_time'])

                # Check if the result is a number
                if is_number(cost):
                    logging.info('Cost: %s', cost)
                    log('%s' % cost.rjust(10))
                    costs[zone] = cost
                else:
                    logging.error('Cost does not appear to be a number')

            # Add the costs to the output object
            if script_args.json is not None:
                operator["costs"] = costs

    except WebDriverException:
        driver.quit()
        raise
    finally:
        # Close and quit the browser
        logging.debug('Closing web driver')
        driver.close()


def load_data(file_name):
    """ Load the data file. """

    parsed_data = None

    # Check whether the file exists
    if not os.path.isfile(file_name):
        logging.error('File \'%s\' does not exist', file_name)
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
            logging.error('Invalid JSON: %s', err)
    finally:
        data_file.close()

    return parsed_data


def init_log():
    """ Initialise the logging. """
    level = script_args.log_level
    log_dir = os.path.abspath(script_args.log_dir)
    logger = logging.getLogger(__name__)
    log_format = (
        '[%(asctime)s] [%(levelname)s] '
        '[%(name)s] [%(funcName)s():%(lineno)s] '
        '[PID:%(process)d] %(message)s')

    if not os.path.isdir(log_dir):
        logging.error('Logging directory \'%s\' does not exist', log_dir)
        sys.exit(os.EX_IOERR)

    dir_re = re.compile(u'/$')
    if not re.match(dir_re, log_dir):
        log_dir += "/"

    # Define the logging stream
    stream = open(log_dir + LOG_FILE, 'w+')

    log_levels = {
        'unset': logging.NOTSET,
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    log_level = log_levels[level]

    coloredlogs.install(
        level=log_level,
        fmt=log_format,
        datefmt='%d/%m/%Y %H:%M:%S',
        stream=stream)

    log('Logging to \'%s\' at level \'%s\'' % (log_dir + LOG_FILE, level))

    return logger


def init_out_file():
    """ Open the output file. """
    script_args.out = os.path.abspath(script_args.out)
    log('Printing output to \'%s\'' % script_args.out)
    if script_args.out is not None:
        try:
            if script_args.json:
                json_re = re.compile(u'.json$')
                if not re.match(json_re, script_args.out):
                    script_args.out += ".json"
            script_args.out = open(script_args.out, 'w')
        except IOError:
            logging.exception(
                'Could not open output file \'%s\'', script_args.out)
            sys.exit(os.EX_IOERR)


def get_args():
    """ Get the command-line arguments. """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
        description=__doc__)

    # Optional args
    parser.add_argument(
        '--data',
        metavar='[file]',
        type=str,
        required=True,
        help=textwrap.dedent("""\
        File containing the operator URL,
        the list of country zones and the file
        structure for the Selenium driver."""))
    parser.add_argument(
        '-h',
        '--help',
        action='help',
        default=argparse.SUPPRESS,
        help=textwrap.dedent("""\
        Show this help message and exit."""))
    parser.add_argument(
        '--json',
        action='store_true',
        help=textwrap.dedent("""\
        Write the results using a JSON format."""))
    parser.add_argument(
        '--log-dir',
        metavar='[dir]',
        type=str,
        default='/tmp/',
        help=textwrap.dedent("""\
        Write log file (.log) to a specific
        folder (default /tmp)."""))
    parser.add_argument(
        '--log-level',
        metavar='[level]',
        default='info',
        type=str,
        help=textwrap.dedent("""\
        Log levels: unset, debug, info, warning,
        error, critical (default info)."""))
    parser.add_argument(
        '-o',
        '--out',
        metavar='[of]',
        type=str,
        help='Write output to file (default STDOUT).')
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='Run in quiet mode.')
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s {0}'.format(__version__),
        help='Show version number.')

    return parser.parse_args()


def main():
    """ Main. """
    try:
        global script_args
        script_args = get_args()
        init_log()
        if script_args.out is not None:
            init_out_file()
        data = load_data(os.path.abspath(script_args.data))
        process_data(data)
        # Print the output in JSON format
        if script_args.json:
            out_file = script_args.out
            if script_args.out is None:
                out_file = sys.stdout
            json.dump(data, fp=out_file,
                      indent=4, encoding='utf-8')

        if script_args.out is not None:
            script_args.out.close()
    # Ctrl-C
    except KeyboardInterrupt, err:
        raise err
    except SystemExit, err:
        raise err
    except:
        print('Unexpected error:', sys.exc_info()[0])
        raise

    return os.EX_OK

if __name__ == '__main__':
    sys.exit(main())
