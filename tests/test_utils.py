import unittest
from aws_lambda_decorators.validators import Mandatory, RegexValidator
from aws_lambda_decorators.utils import is_type_in_list


class UtilsTests(unittest.TestCase):

    def test_is_type_in_list_returns_false_if_item_of_type_missing(self):
        items = [Mandatory, Mandatory, Mandatory]
        self.assertFalse(is_type_in_list(RegexValidator, items))

    def test_is_type_in_list_returns_true_if_item_of_type_exists(self):
        items = [Mandatory, RegexValidator(), Mandatory]
        self.assertTrue(is_type_in_list(RegexValidator, items))
