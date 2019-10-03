import unittest
from aws_lambda_decorators.classes import Parameter


class ParamTests(unittest.TestCase):

    def test_annotations_from_key_returns_none_when_no_annotations(self):
        key = "simple"
        response = Parameter.get_annotations_from_key(key)
        self.assertTrue(response[0] == "simple")
        self.assertTrue(response[1] is None)

    def test_annotations_from_key_returns_annotation(self):
        key = "simple[annotation]"
        response = Parameter.get_annotations_from_key(key)
        self.assertTrue(response[0] == "simple")
        self.assertTrue(response[1] == "annotation")
