import pytest
from user_interface import display_report, download_report, authenticate_user, handle_error

def test_display_report():
    # Assuming display_report should raise an exception if no report is provided
    with pytest.raises(ValueError):
        display_report(None)

def test_download_report():
    # Assuming download_report should raise an exception if no report is provided
    with pytest.raises(ValueError):
        download_report(None)

def test_authenticate_user():
    # Assuming authenticate_user should raise an exception if the user is not authorized
    with pytest.raises(PermissionError):
        authenticate_user("unauthorized_user")

def test_handle_error():
    # Assuming handle_error should raise an exception if no error message is provided
    with pytest.raises(ValueError):
        handle_error(None)
