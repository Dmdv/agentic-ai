import pytest
from data_ingestion import process_data

def test_process_data_invalid_type():
    with pytest.raises(TypeError):
        process_data(123)

def test_process_data_empty_data():
    with pytest.raises(ValueError):
        process_data({})

def test_process_data_missing_required_fields():
    with pytest.raises(KeyError):
        process_data({'name': 'John'})

def test_process_data_incorrect_data_format():
    with pytest.raises(ValueError):
        process_data({'name': 'John', 'age': 'thirty'})

def test_process_data_unexpected_data_values():
    with pytest.raises(ValueError):
        process_data({'name': 'John', 'age': -5})
