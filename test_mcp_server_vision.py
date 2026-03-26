import unittest
from unittest.mock import patch, MagicMock
from mcp_server_vision import VisionServer

class TestMcpServerVision(unittest.TestCase):
    @patch('mlx_vlm.load')
    @patch('mlx_vlm.generate')
    @patch('builtins.open', new_callable=MagicMock)
    def test_analyze_image(self, mock_open, mock_generate, mock_load):
        mock_model = MagicMock()
        mock_processor = MagicMock()
        mock_load.return_value = (mock_model, mock_processor)
        mock_processor.apply_chat_template.return_value = "prompt_text"
        mock_generate.return_value = "analysis_output"
        
        vision_server = VisionServer()
        result = vision_server.analyze_image("image_path", "prompt")
        
        self.assertEqual(result, "analysis_output")
        mock_load.assert_called_once_with("mlx-community/Qwen2.5-VL-7B-Instruct-4bit")
        mock_processor.apply_chat_template.assert_called_once_with(
            [{"role": "user", "content": [{"type": "image", "url": "image_path"}, {"type": "text", "text": "prompt"}]}],
            tokenize=False,
            add_generation_prompt=True
        )
        mock_generate.assert_called_once_with(
            mock_model,
            mock_processor,
            "prompt_text",
            max_tokens=1000,
            verbose=False
        )

if __name__ == "__main__":
    unittest.main()
