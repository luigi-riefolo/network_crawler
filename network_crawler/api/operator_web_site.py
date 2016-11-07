#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging

try:
    from selenium.common.exceptions import NoSuchElementException
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
except ImportError as imp_err:
    raise ImportError('Failed to import \'selenium\':\n' + str(imp_err))


"""
Network operator's website API.
"""


class OperatorWebSite(object):
    """
    A network operator's website class.

    Attributes:
        @param driver: Selenium webdriver.
        @param data: Dict containing the URL, the list of actions,
                     the list of country zones and th time to wait
                     for a page element page to be loaded.

    It implements a series of methods used to perfom
    specific action on a network operator's website.
    """

    def __init__(self, driver, data):
        """ """
        self.driver = driver
        self.url = data['url']
        self.actions = data['actions']
        self.zones = data['zones']
        self.load_time = data['load_time']

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
        element = self.get_element(self.driver, path)
        if element is None:
            return False

        ret = False
        attr = self.get_attr(element, method_name)
        # Function attribute
        if hasattr(attr, '__call__'):
            # Function invocation
            if args is not None:
                attr(args)
            else:
                attr()

            ret = True
        # Property attribute
        else:
            ret = attr

        return ret

    def type_zone(self, args):
        """
        Types a zone name into a selected input.

        The input element is selected using the given XPath.
        """
        logging.debug('Executing \'type_zone\' action for '
                      '\'%s\', input \'%s\'',
                      args['path'], args['zone'])
        keys = args['zone'] + Keys.RETURN
        return self.run_element_method(args['path'], 'send_keys', keys)

    def click(self, args):
        """
        Executes a click action.

        The input element is selected using the given XPath.
        """
        logging.debug('Executing \'click\' action for \'%s\'', args['path'])
        return self.run_element_method(args['path'], 'click')

    def get_cost(self, args):
        """
        Returns the calling cost.

        The cost is represented as text within the current element.
        The input element is selected using the given XPath.
        """
        logging.debug('Executing \'get_cost\' action for \'%s\'', args['path'])
        return self.run_element_method(args['path'], 'text')

    @staticmethod
    def get_attr(obj, name):
        """
        Return an object attribute.

        Utility function, it checks whether an attribute exists and returns it.
        Otherwise an AttributeError exception is thrown.
        """
        attr = None
        try:
            attr = getattr(obj, name)
        except AttributeError:
            class_name = obj.__class__.__name__
            err_msg = ('Class \'{}\' '
                       'does not contain \'{}\'\n').format(class_name, name)
            logging.exception(err_msg)

        return attr

    def get_element(self, driver, path):
        """ Wait for an element to be loaded and return it. """
        element = None
        try:
            el_to_load = EC.presence_of_element_located((By.XPATH, path))
            element = WebDriverWait(driver, self.load_time).until(el_to_load)

        except NoSuchElementException:
            print('Could not find element %s' % path)
        except TimeoutException:
            print('Loading took too much time')

        return element
