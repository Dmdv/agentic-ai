import unittest
from sdd_test_output.input_module import InputModule, receive_user_request

class TestInputModule(unittest.TestCase):
    def test_get_input(self):
        input_module = InputModule()
        # Expected to fail because get_input returns "sample input" not "expected input"
        self.assertEqual(input_module.get_input(), "expected input")

    def test_receive_user_request(self):
        # Expected to fail because receive_user_request returns "user request" not "expected request"
        self.assertEqual(receive_user_request(), "expected request")

if __name__ == '__main__':
    unittest.main()
