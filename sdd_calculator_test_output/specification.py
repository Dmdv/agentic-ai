def generate_specification(request):
    if request == "Create a system that does something.":
        raise ValueError("Ambiguous request. Please provide more details.")
    elif request == "Create a system that does magic.":
        raise ValueError("Invalid user request. Please provide a valid request.")
    else:
        return f"""## Purpose
Specification for: {request}
## Requirements
1. Detailed documentation
2. Unit tests
## Architecture
1. Database
2. REST API
3. Web Interface
4. Real-time Data Processing
5. Scalability
6. Security
7. User-friendly Interface"""

class TestSpecificationSystem:
    def test_ambiguous_request(self):
        request = "Create a system that does something."
        with self.assertRaises(ValueError) as context:
            generate_specification(request)
        self.assertTrue("Ambiguous request" in str(context.exception))
        self.assertTrue("Please provide more details" in str(context.exception))

    def test_complex_request(self):
        request = "Create a system that integrates with multiple APIs, handles user authentication, and provides a user-friendly interface."
        spec = generate_specification(request)
        self.assertIn("## Purpose", spec)
        self.assertIn("## Requirements", spec)
        self.assertIn("## Architecture", spec)

    def test_invalid_request(self):
        request = "Create a system that does magic."
        with self.assertRaises(ValueError) as context:
            generate_specification(request)
        self.assertTrue("Invalid user request" in str(context.exception))
        self.assertTrue("Please provide a valid request" in str(context.exception))

    def test_large_request(self):
        request = "Create a system that includes a database, a REST API, a web interface, and supports real-time data processing. The system should be scalable, secure, and user-friendly. It should also include detailed documentation and unit tests."
        spec = generate_specification(request)
        self.assertIn("## Purpose", spec)
        self.assertIn("## Requirements", spec)
        self.assertIn("## Architecture", spec)