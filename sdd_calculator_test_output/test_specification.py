import unittest
from specification_system import generate_specification

class TestSpecificationSystem(unittest.TestCase):

    def test_ambiguous_request(self):
        request = "Create a system that does something."
        with self.assertRaises(ValueError) as context:
            generate_specification(request)
        self.assertEqual(str(context.exception), "User request is ambiguous. Please provide more details.")

    def test_complex_request(self):
        request = "Create a system that integrates with multiple APIs, handles user authentication, and provides a user-friendly interface."
        spec = generate_specification(request)
        self.assertIn("## Purpose", spec)
        self.assertIn("## Requirements", spec)
        self.assertIn("## Architecture", spec)
        self.assertIn("## Edge Cases", spec)
        self.assertIn("Integrating with multiple APIs", spec)
        self.assertIn("User authentication", spec)
        self.assertIn("User-friendly interface", spec)

    def test_invalid_request(self):
        request = "Create a system that does magic."
        with self.assertRaises(ValueError) as context:
            generate_specification(request)
        self.assertEqual(str(context.exception), "Invalid user request. Please provide a valid request.")

    def test_large_request(self):
        request = "Create a system that includes a database, a REST API, a web interface, and supports real-time data processing. The system should be scalable, secure, and user-friendly. It should also include detailed documentation and unit tests."
        spec = generate_specification(request)
        self.assertIn("## Purpose", spec)
        self.assertIn("## Requirements", spec)
        self.assertIn("## Architecture", spec)
        self.assertIn("## Edge Cases", spec)
        self.assertIn("database", spec)
        self.assertIn("REST API", spec)
        self.assertIn("web interface", spec)
        self.assertIn("real-time data processing", spec)
        self.assertIn("scalable", spec)
        self.assertIn("secure", spec)
        self.assertIn("user-friendly", spec)
        self.assertIn("detailed documentation", spec)
        self.assertIn("unit tests", spec)

if __name__ == '__main__':
    unittest.main()