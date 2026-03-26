import unittest
from unittest.mock import patch, MagicMock
from mcp_sdd_swarm import SDDSwarmOrchestrator

class TestSddSwarmOrchestrator(unittest.TestCase):
    @patch('mcp_sdd_swarm.load')
    @patch('mcp_sdd_swarm.generate')
    @patch('mcp_sdd_swarm.stdio_client')
    @patch('mcp_sdd_swarm.ClientSession')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('os.path.exists', return_value=True)
    @patch('os.walk', return_value=[('agents', [], ['agent1.md', 'agent2.md'])])
    def test_run(self, mock_walk, mock_exists, mock_open, mock_client_session, mock_stdio_client, mock_generate, mock_load):
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        mock_load.return_value = (mock_model, mock_tokenizer)
        mock_generate.return_value = "response"
        mock_session = MagicMock()
        mock_session.initialize.return_value = None
        mock_session.list_tools.return_value = MagicMock(tools=[])
        mock_session.call_tool.return_value = MagicMock(content=[MagicMock(text="tool_result")])
        mock_stdio_client.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        mock_stdio_client.return_value.__aenter__.return_value.__aenter__.return_value = mock_session
        
        swarm = SDDSwarmOrchestrator(architect_model="architect_model", engineer_model="engineer_model")
        asyncio.run(swarm.run(user_prompt="user_prompt"))
        
        mock_load.assert_called_once_with("architect_model")
        mock_generate.assert_called_once()
        mock_stdio_client.assert_called()
        mock_session.initialize.assert_called_once()
        mock_session.list_tools.assert_called_once()
        mock_session.call_tool.assert_called_once()
        mock_open.assert_called()
        mock_walk.assert_called_once_with("agents")
        mock_exists.assert_called()

if __name__ == "__main__":
    unittest.main()
