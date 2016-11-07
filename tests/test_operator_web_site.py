"""OperatorWebSite class unit test."""


from __init__ import json, os, time, unittest, \
    webdriver, WebDriverException, OperatorWebSite


class TestOperatorWebSite(unittest.TestCase):
    """Unit test class for OperatorWebSite."""

    def load_data(self):
        """ Load the data file. """

        self.data = None
        file_name = os.path.abspath("data/sites/operators.json")
        file_data = None

        # Check whether the file exists
        self.assertTrue(os.path.isfile(file_name), 'Invalid data file')

        # Open the file and load its data
        try:
            file_data = open(file_name, 'r')
        except (IOError, OSError) as err:
            raise err
        else:
            try:
                # Load the data file into a JSON object
                self.data = json.loads(file_data.read())["operators"][0]
                self.assertIsNotNone(self.data)
            except ValueError as err:
                raise err
        finally:
            file_data.close()

    def setUp(self):
        """Setup."""
        try:
            # Chrome driver
            self.driver = webdriver.Chrome()
            self.load_data()
            # Create the operator web site object
            self.operator_obj = OperatorWebSite(self.driver, self.data)
            self.assertIsNotNone(
                self.operator_obj, 'Could not creat OperatorWebSite object')
            self.driver.get(self.data["url"])
        except WebDriverException:
            self.driver.quit()
            raise

    def tearDown(self):
        """Tear down."""
        # Close and quit the browser
        self.driver.close()

    def run_action(self, action_name, action_args=None):
        """Run a specific OperatorWebSite action."""
        # Execute the requested web driver action
        method = self.operator_obj.get_attr(
            self.operator_obj, action_name)
        self.assertIsNotNone(
            method, 'Failed to get method \'%s\'' % action_name)

        res = method(action_args)
        self.assertIsNotNone(res, ('Action \'%s\' failed', action_name))
        time.sleep(3)

        return res

    def test_type_zone(self):
        args = {
            'path': self.data['actions'][0]['type_zone'],
            'zone': self.data['zones'][0]}
        action = 'type_zone'
        res = self.run_action(action, args)
        self.assertTrue(res, ('Action \'%s\' failed', action))

    def test_click(self):
        self.test_type_zone()
        action = 'click'
        args = {'path': self.data['actions'][1][action]}
        res = self.run_action(action, args)
        self.assertTrue(res, ('Action \'%s\' failed', action))

    def test_get_cost(self):
        self.test_type_zone()
        self.test_click()
        action = 'get_cost'
        args = {'path': self.data['actions'][2][action]}
        res = self.run_action(action, args)
        self.assertTrue(res, ('Action \'%s\' failed', action))

    def test_not_action(self):
        self.assertRaises(AssertionError, self.run_action, "not_action")


if __name__ == '__main__':
    unittest.main()
