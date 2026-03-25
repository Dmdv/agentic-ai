# Technical Specification
## Goal
1. Run the tests in the `test_project/tests/` directory to identify any broken tests.
2. Fix the bugs in the source code located in `test_project/src/`.
3. Write a `Dockerfile` in the `test_project` directory to containerize the application.

## Architecture
1. **Testing**: Use the `pytest` framework to execute the tests in `test_project/tests/`.
2. **Bug Fixing**: Analyze the test failures and update the corresponding functions in `test_project/src/`.
3. **Containerization**: Create a `Dockerfile` in the `test_project` directory to ensure the application can be run in a Docker container.