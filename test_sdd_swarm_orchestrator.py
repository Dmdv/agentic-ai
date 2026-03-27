import unittest
from unittest.mock import patch, MagicMock
from mcp_sdd_swarm import SDDSwarmOrchestrator
from unittest import IsolatedAsyncioTestCase


class TestSDDSwarmOrchestrator(IsolatedAsyncioTestCase):

    @patch('mcp_sdd_swarm.load')
    @patch('mcp_sdd_swarm.MCPAgenticLoop')
    def test_init(self, mock_mcp_agentic_loop, mock_load):
        # Arrange
        architect_model = 'architect_model'
        engineer_model = 'engineer_model'
        
        # Act
        orchestrator = SDDSwarmOrchestrator(architect_model, engineer_model)
        
        # Assert
        self.assertEqual(orchestrator.architect_model_name, architect_model)
        self.assertEqual(orchestrator.engineer_model_name, engineer_model)
        self.assertIsNone(orchestrator._architect)
        self.assertIsNone(orchestrator._architect_tokenizer)
        self.assertIsNone(orchestrator._engineer_agent)
        self.assertIsNotNone(orchestrator.hive_mind)
        
    @patch('mcp_sdd_swarm.load')
    def test_get_architect(self, mock_load):
        # Arrange
        architect_model = 'architect_model'
        engineer_model = 'engineer_model'
        orchestrator = SDDSwarmOrchestrator(architect_model, engineer_model)
        mock_load.return_value = ('architect', 'architect_tokenizer')
        
        # Act
        architect, architect_tokenizer = orchestrator._get_architect()
        
        # Assert
        self.assertEqual(architect, 'architect')
        self.assertEqual(architect_tokenizer, 'architect_tokenizer')
        mock_load.assert_called_once_with(architect_model)
        
    @patch('mcp_sdd_swarm.MCPAgenticLoop')
    def test_get_engineer_agent(self, mock_mcp_agentic_loop):
        # Arrange
        architect_model = 'architect_model'
        engineer_model = 'engineer_model'
        orchestrator = SDDSwarmOrchestrator(architect_model, engineer_model)
        mock_mcp_agentic_loop.return_value = MagicMock()
        
        # Act
        engineer_agent = orchestrator._get_engineer_agent()
        
        # Assert
        self.assertIsNotNone(engineer_agent)
        mock_mcp_agentic_loop.assert_called_once_with(model_name=engineer_model, keep_in_memory=True)
        engineer_agent._load_model.assert_called_once()
        
    @patch('mcp_sdd_swarm.asyncio.sleep', return_value=None)
    @patch('mcp_sdd_swarm.SDDSwarmOrchestrator._get_engineer_agent')
    @patch('mcp_sdd_swarm.HiveMemory')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('os.path.exists', return_value=True)
    async def test_run_spec_phase(self, mock_os_path_exists, mock_open, mock_hive_memory, mock_get_engineer_agent, mock_sleep):
        # Arrange
        architect_model = 'architect_model'
        engineer_model = 'engineer_model'
        orchestrator = SDDSwarmOrchestrator(architect_model, engineer_model)
        user_prompt = 'user_prompt'
        engineer_agent = MagicMock()
        mock_get_engineer_agent.return_value = engineer_agent
        engineer_agent.run = MagicMock()
        engineer_agent.set_persona = MagicMock()
        
        # Act
        await orchestrator._run_spec_phase(user_prompt)
        
        # Assert
        engineer_agent.set_persona.assert_called_with('agents/core/spec-writer.md')
        engineer_agent.run.assert_called_once()
        engineer_agent.set_persona.assert_called_with('agents/core/researcher.md')
        engineer_agent.run.assert_called_with(user_prompt='Read the current SPEC.md. Use your fetch tool to research best practices on the web. If there are flaws, list them. If it is perfect, output "RESEARCH PASSED". Write your findings to RESEARCH_REPORT.md.')
        engineer_agent.set_persona.assert_called_with('agents/core/critical-reviewer.md')
        engineer_agent.run.assert_called_with(user_prompt='Read SPEC.md and RESEARCH_REPORT.md. Review them rigorously. Write your findings and any requested changes to REVIEW_REPORT.md. If there are 0 issues, output exactly "REVIEW PASSED" in the file.')
        engineer_agent.set_persona.assert_called_with('agents/core/spec-writer.md')
        engineer_agent.run.assert_called_with(user_prompt='Read REVIEW_REPORT.md and RESEARCH_REPORT.md. Update SPEC.md to resolve all issues.')
        
    @patch('mcp_sdd_swarm.load')
    @patch('mcp_sdd_swarm.HiveMemory')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('os.path.exists', return_value=True)
    async def test_run_planning_phase(self, mock_os_path_exists, mock_open, mock_hive_memory, mock_load):
        # Arrange
        architect_model = 'architect_model'
        engineer_model = 'engineer_model'
        orchestrator = SDDSwarmOrchestrator(architect_model, engineer_model)
        mock_load.return_value = ('architect', MagicMock())
        mock_open.return_value.__enter__.return_value.read.return_value = 'repo_map_content'
        mock_open.return_value.__enter__.return_value.read.return_value = 'spec_content'
        mock_open.return_value.__enter__.return_value.read.return_value = 'agents/core/planning-agent.md'
        
        # Act
        steps = await orchestrator._run_planning_phase()
        
        # Assert
        self.assertEqual(steps, [{'task': 'Implement SPEC.md', 'agent': None}])
        
    @patch('mcp_sdd_swarm.asyncio.sleep', return_value=None)
    @patch('mcp_sdd_swarm.SDDSwarmOrchestrator._get_engineer_agent')
    @patch('mcp_sdd_swarm.HiveMemory')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('os.path.exists', return_value=True)
    async def test_execute_single_task(self, mock_os_path_exists, mock_open, mock_hive_memory, mock_get_engineer_agent, mock_sleep):
        # Arrange
        architect_model = 'architect_model'
        engineer_model = 'engineer_model'
        orchestrator = SDDSwarmOrchestrator(architect_model, engineer_model)
        task_info = {'task': 'task', 'agent': 'agent.md'}
        preloaded_model = 'preloaded_model'
        preloaded_tokenizer = MagicMock()
        preloaded_tokenizer.apply_chat_template = MagicMock(return_value='formatted_prompt')
        step_num = 1
        engineer_agent = MagicMock()
        mock_get_engineer_agent.return_value = engineer_agent
        engineer_agent.run = MagicMock()
        engineer_agent.set_persona = MagicMock()
        
        # Act
        lesson = await orchestrator._execute_single_task(task_info, preloaded_model, preloaded_tokenizer, step_num)
        
        # Assert
        engineer_agent.set_persona.assert_called_with('agents/agent.md')
        engineer_agent.run.assert_called_once()
        engineer_agent.set_persona.assert_called_with('agents/qa/requirement-validator.md')
        engineer_agent.run.assert_called_with(user_prompt='Validate that the recent code changes fulfill this task: task and align with SPEC.md. Save your findings to VALIDATION_1.md')
        engineer_agent.set_persona.assert_called_with('agents/core/critical-reviewer.md')
        engineer_agent.run.assert_called_with(user_prompt='Read VALIDATION_1.md and review the latest code changes. If there are issues, use bash to fix them, or leave instructions. Save final status to REVIEW_REPORT_1.md. Finally, write a 1-sentence "Lesson Learned" about any bugs you fixed to LESSONS_1.txt.')
        self.assertEqual(lesson, 'Lesson Learned')
        
    @patch('mcp_sdd_swarm.asyncio.sleep', return_value=None)
    @patch('mcp_sdd_swarm.SDDSwarmOrchestrator._get_engineer_agent')
    @patch('mcp_sdd_swarm.HiveMemory')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('os.path.exists', return_value=True)
    async def test_run_execution_phase(self, mock_os_path_exists, mock_open, mock_hive_memory, mock_get_engineer_agent, mock_sleep):
        # Arrange
        architect_model = 'architect_model'
        engineer_model = 'engineer_model'
        orchestrator = SDDSwarmOrchestrator(architect_model, engineer_model)
        steps = [{'task': 'task1', 'agent': 'agent1.md'}, {'task': 'task2', 'agent': 'agent2.md'}]
        preloaded_model = 'preloaded_model'
        preloaded_tokenizer = MagicMock()
        preloaded_tokenizer.apply_chat_template = MagicMock(return_value='formatted_prompt')
        engineer_agent = MagicMock()
        mock_get_engineer_agent.return_value = engineer_agent
        engineer_agent.run = MagicMock()
        engineer_agent.set_persona = MagicMock()
        
        # Act
        await orchestrator._run_execution_phase(steps)
        
        # Assert
        engineer_agent.set_persona.assert_called_with('agents/agent1.md')
        engineer_agent.run.assert_called_once()
        engineer_agent.set_persona.assert_called_with('agents/qa/requirement-validator.md')
        engineer_agent.run.assert_called_with(user_prompt='Validate that the recent code changes fulfill this task: task1 and align with SPEC.md. Save your findings to VALIDATION_1.md')
        engineer_agent.set_persona.assert_called_with('agents/core/critical-reviewer.md')
        engineer_agent.run.assert_called_with(user_prompt='Read VALIDATION_1.md and review the latest code changes. If there are issues, use bash to fix them, or leave instructions. Save final status to REVIEW_REPORT_1.md. Finally, write a 1-sentence "Lesson Learned" about any bugs you fixed to LESSONS_1.txt.')
        engineer_agent.set_persona.assert_called_with('agents/agent2.md')
        engineer_agent.run.assert_called_once()
        engineer_agent.set_persona.assert_called_with('agents/qa/requirement-validator.md')
        engineer_agent.run.assert_called_with(user_prompt='Validate that the recent code changes fulfill this task: task2 and align with SPEC.md. Save your findings to VALIDATION_2.md')
        engineer_agent.set_persona.assert_called_with('agents/core/critical-reviewer.md')
        engineer_agent.run.assert_called_with(user_prompt='Read VALIDATION_2.md and review the latest code changes. If there are issues, use bash to fix them, or leave instructions. Save final status to REVIEW_REPORT_2.md. Finally, write a 1-sentence "Lesson Learned" about any bugs you fixed to LESSONS_2.txt.')
        
if __name__ == '__main__':
    unittest.main()
