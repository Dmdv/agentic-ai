import unittest
from unittest.mock import patch, MagicMock
from mcp_server_diff import apply_diff

class TestMcpServerDiff(unittest.TestCase):
    @patch('builtins.open', new_callable=MagicMock)
    def test_apply_diff(self, mock_open):
        mock_open.side_effect = [
            MagicMock(read=MagicMock(return_value="line1\nline2\nline3\nline4\n")),
            MagicMock(write=MagicMock())
        ]
        
        content = "line1\nline2\nline3\nline4\n"
        search_block = "line2\nline3\n"
        replace_block = "line2_new\nline3_new\n"
        expected = "line1\nline2_new\nline3_new\nline4\n"
        
        new_content = apply_diff(content, search_block, replace_block)
        self.assertEqual(new_content, expected)

if __name__ == "__main__":
    unittest.main()
