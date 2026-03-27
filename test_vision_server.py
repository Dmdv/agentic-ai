import unittest
from unittest.mock import patch, MagicMock
from mcp_server_vision import VisionServer, handle_call_tool


class TestVisionServer(unittest.TestCase):

    def setUp(self):
        self.vision_server = VisionServer()

    def test_initialization(self):
        self.assertEqual(self.vision_server.model_name, 'mlx-community/Qwen2.5-VL-7B-Instruct-4bit')
        self.assertIsNone(self.vision_server.model)
        self.assertIsNone(self.vision_server.processor)

    @patch('mcp_server_vision.load')
    def test_load(self, mock_load):
        mock_load.return_value = ('mock_model', 'mock_processor')
        self.vision_server._load()
        self.assertEqual(self.vision_server.model, 'mock_model')
        self.assertEqual(self.vision_server.processor, 'mock_processor')

    @patch('mcp_server_vision.load')
    @patch('mcp_server_vision.generate')
    def test_analyze_image_invalid_path(self, mock_generate, mock_load):
        mock_load.return_value = ('mock_model', 'mock_processor')
        mock_generate.side_effect = Exception('Image file not found')
        with self.assertRaises(Exception) as context:
            self.vision_server.analyze_image('non_existent_image.jpg', 'Check if the image matches the spec.')
        self.assertTrue('Image file not found' in str(context.exception))

    @patch('mcp_server_vision.load')
    @patch('mcp_server_vision.generate')
    def test_analyze_image_valid_path_invalid_generate(self, mock_generate, mock_load):
        mock_load.return_value = ('mock_model', 'mock_processor')
        mock_generate.side_effect = Exception('Mocked generate error')
        with self.assertRaises(Exception) as context:
            self.vision_server.analyze_image('valid_image.jpg', 'Check if the image matches the spec.')
        self.assertTrue('Mocked generate error' in str(context.exception))

    @patch('mcp_server_vision.load')
    @patch('mcp_server_vision.generate')
    def test_handle_call_tool_invalid_tool(self, mock_generate, mock_load):
        mock_load.return_value = ('mock_model', 'mock_processor')
        mock_generate.return_value = 'Mocked generate output'
        with self.assertRaises(ValueError) as context:
            handle_call_tool('invalid_tool', {'image_path': 'valid_image.jpg', 'prompt': 'Check if the image matches the spec.'})
        self.assertTrue('Unknown tool: invalid_tool' in str(context.exception))

if __name__ == '__main__':
    unittest.main()
