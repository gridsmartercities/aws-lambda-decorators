import unittest
from aws_lambda_decorators.classes import Parameter, SSMParameter, BaseParameter


class ParamTests(unittest.TestCase):

    def test_can_create_base_parameter(self):
        base_param = BaseParameter("var_name")
        self.assertEqual("var_name", base_param.get_var_name())

    def test_annotations_from_key_returns_annotation(self):
        key = "simple[annotation]"
        response = Parameter.get_annotations_from_key(key)
        self.assertTrue(response[0] == "simple")
        self.assertTrue(response[1] == "annotation")

    def test_can_not_add_non_pythonic_var_name_to_ssm_parameter(self):
        param = SSMParameter("tests", "with space")

        with self.assertRaises(SyntaxError):
            param.get_var_name()
