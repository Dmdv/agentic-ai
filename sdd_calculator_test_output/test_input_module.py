import pytest
from input_module import receive_user_request

def test_ambiguous_input():
    with pytest.raises(ValueError) as e:
        receive_user_request('Create a system that does something.')
    assert str(e.value) == 'User request is ambiguous. Please provide more details.'

def test_invalid_input():
    with pytest.raises(ValueError) as e:
        receive_user_request('Invalid request!')
    assert str(e.value) == 'Invalid user request. Please provide a valid request.'

def test_valid_input():
    response = receive_user_request('Create a system that manages user data.')
    assert '## Purpose' in response
    assert '## Requirements' in response
    assert '## Architecture' in response
    assert '## Edge Cases' in response

def test_empty_input():
    with pytest.raises(ValueError) as e:
        receive_user_request('')
    assert str(e.value) == 'User request is empty. Please provide a valid request.'