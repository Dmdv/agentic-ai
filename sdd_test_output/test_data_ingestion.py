import unittest
from unittest.mock import patch
from sdd_test_output.data_ingestion import DataIngestion

class TestDataIngestion(unittest.TestCase):
    @patch.object(DataIngestion, 'connect_to_database')
    def test_connect_to_database(self, mock_connect):
        di = DataIngestion()
        di.connect_to_database()
        mock_connect.assert_called_once()

    @patch.object(DataIngestion, 'make_api_request')
    def test_make_api_request(self, mock_request):
        di = DataIngestion()
        di.make_api_request()
        mock_request.assert_called_once()

    @patch.object(DataIngestion, 'read_file')
    def test_read_file(self, mock_read):
        di = DataIngestion()
        di.read_file('test_path')
        mock_read.assert_called_once_with('test_path')

    @patch.object(DataIngestion, 'ingest_from_database')
    def test_ingest_from_database(self, mock_ingest):
        di = DataIngestion()
        di.ingest_from_database()
        mock_ingest.assert_called_once()

    def test_process_data(self):
        di = DataIngestion()
        self.assertEqual(di.process_data('test'), 'TEST')
        with self.assertRaises(TypeError):
            di.process_data(123)
        with self.assertRaises(ValueError):
            di.process_data('')

if __name__ == '__main__':
    unittest.main()
