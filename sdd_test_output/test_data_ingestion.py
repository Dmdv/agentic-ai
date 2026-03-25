import pytest
from unittest.mock import patch, MagicMock
from data_ingestion import DataIngestion


def test_ingest_from_database_failure():
    ingestion = DataIngestion()
    with patch('data_ingestion.DataIngestion.connect_to_database', side_effect=Exception('Database connection failed')):
        with pytest.raises(Exception) as e:
            ingestion.ingest_from_database()
        assert str(e.value) == 'Database connection failed'


def test_ingest_from_api_failure():
    ingestion = DataIngestion()
    with patch('data_ingestion.DataIngestion.make_api_request', side_effect=Exception('API request failed')):
        with pytest.raises(Exception) as e:
            ingestion.ingest_from_api()
        assert str(e.value) == 'API request failed'


def test_ingest_from_file_failure():
    ingestion = DataIngestion()
    with patch('data_ingestion.DataIngestion.read_file', side_effect=Exception('File read failed')):
        with pytest.raises(Exception) as e:
            ingestion.ingest_from_file('test_file.csv')
        assert str(e.value) == 'File read failed'


def test_handle_data_source_failure():
    ingestion = DataIngestion()
    with patch('data_ingestion.DataIngestion.ingest_from_database', side_effect=Exception('Incomplete data')):
        with pytest.raises(Exception) as e:
            ingestion.ingest_from_database()
        assert str(e.value) == 'Incomplete data'