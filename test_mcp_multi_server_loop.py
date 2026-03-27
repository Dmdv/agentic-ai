from unittest.mock import MagicMock, patch
class TestMcpAgenticLoop:
    @patch('mcp_multi_server_loop.load')
    @patch('mcp_multi_server_loop.generate')
    @patch('mcp_multi_server_loop.stdio_client')
    @patch('mcp_multi_server_loop.ClientSession')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('os.path.exists', return_value=True)
    @patch('os.walk', return_value=[('agents', [], ['agent1.md', 'agent2.md'])])
    def test_run(self, mock_walk, mock_exists, mock_open, mock_client_session, mock_stdio_client, mock_generate, mock_load):
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        mock_load.return_value = (mock_model, mock_tokenizer)
        mock_generate.return_value = 'response'
        mock_session = MagicMock()
        mock_session.initialize.return_value = None
        mock_session.list_tools.return_value = MagicMock(tools=[])
        mock_session.call_tool.return_value = MagicMock(content=[MagicMock(text='tool_result')])
        
        # Correct the mock setup for stdio_client
        mock_stdio_client.return_value.__aenter__.return_value = mock_session
        
        # Run the test
        # Assuming the function to test is `run` in `mcp_multi_server_loop`
        from mcp_multi_server_loop import run
        run()
