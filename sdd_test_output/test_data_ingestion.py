import pytest
from sdd_test_output.data_ingestion import DataIngestion

class TestDataIngestion:
    def test_connect_to_database(self):
        data_ingestion = DataIngestion()
        with pytest.raises(NotImplementedError):
            data_ingestion.connect_to_database()

    def test_make_api_request(self):
        data_ingestion = DataIngestion()
        with pytest.raises(NotImplementedError):
            data_ingestion.make_api_request()

    def test_read_file(self):
        data_ingestion = DataIngestion()
        with pytest.raises(NotImplementedError):
            data_ingestion.read_file("some_file_path")

    def test_ingest_from_database(self):
        data_ingestion = DataIngestion()
        with pytest.raises(NotImplementedError):
            data_ingestion.ingest_from_database()

    def test_process_data_with_non_string(self):
        data_ingestion = DataIngestion()
        with pytest.raises(TypeError):
            data_ingestion.process_data(123)

    def test_process_data_with_empty_string(self):
        data_ingestion = DataIngestion()
        with pytest.raises(ValueError):
            data_ingestion.process_data("")

    def test_process_data_with_valid_string(self):
        data_ingestion = DataIngestion()
        result = data_ingestion.process_data("test")
        assert result == "test"  # This will fail
