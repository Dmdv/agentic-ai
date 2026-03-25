import pytest
from unittest.mock import patch
from report_generation import generate_report

def test_generate_report_empty_data():
    with pytest.raises(ValueError) as excinfo:
        generate_report({})
    assert 'Empty data provided' in str(excinfo.value)

def test_generate_report_invalid_data():
    with pytest.raises(ValueError) as excinfo:
        generate_report({'invalid_key': 'invalid_value'})
    assert 'Invalid data provided' in str(excinfo.value)

def test_generate_report_large_data():
    large_data = [{'key': f'value_{i}'} for i in range(1000000)]
    with pytest.raises(Exception) as excinfo:
        generate_report(large_data)
    assert 'Failed to generate report' in str(excinfo.value)

def test_generate_report_unsupported_format():
    with pytest.raises(ValueError) as excinfo:
        generate_report({}, format='unsupported')
    assert 'Unsupported format' in str(excinfo.value)

def test_generate_report_file_write_failure():
    with patch('builtins.open', side_effect=IOError('File write failed')):
        with pytest.raises(IOError) as excinfo:
            generate_report({})
        assert 'File write failed' in str(excinfo.value)
