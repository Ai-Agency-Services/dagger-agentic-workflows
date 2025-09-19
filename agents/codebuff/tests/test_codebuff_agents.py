"""Comprehensive unit tests for Codebuff agent functionality."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))


class TestCodebuffCreation:
    """Test Codebuff agent creation and initialization."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('agents.codebuff.src.codebuff.main.yaml.safe_load')
    async def test_create_codebuff_success(self, mock_yaml_load):
        """Test successful Codebuff creation."""
        from codebuff.main import Codebuff
        
        mock_config = {
            "container": {
                "work_dir": "/app",
                "docker_file_path": "./Dockerfile"
            },
            "core_api": {
                "model": "gpt-4o",
                "provider": "openai"
            }
        }
        mock_yaml_load.return_value = mock_config
        
        mock_file = AsyncMock()
        mock_file.contents = AsyncMock(return_value="config content")
        
        codebuff = await Codebuff.create(config_file=mock_file)
        
        assert codebuff.config == mock_config
        assert codebuff.config_file == mock_file
        assert codebuff.container is None
        assert codebuff.github_token is None
        assert codebuff.model is None

    @pytest.mark.unit
    def test_get_model_for_agent_specific_config(self):
        """Test getting model for agent with specific configuration."""
        from codebuff.main import Codebuff
        
        config = {
            "agents": {
                "file_explorer": {
                    "model": "gpt-4o-mini"
                }
            },
            "core_api": {
                "model": "gpt-4o"
            }
        }
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = config
        codebuff._get_model_for_agent = Codebuff._get_model_for_agent.__get__(codebuff, Codebuff)
        
        model = codebuff._get_model_for_agent("file_explorer")
        assert model == "gpt-4o-mini"

    @pytest.mark.unit
    def test_get_model_for_agent_core_api_fallback(self):
        """Test getting model with core_api fallback."""
        from codebuff.main import Codebuff
        
        config = {
            "core_api": {
                "model": "gpt-4o"
            }
        }
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = config
        codebuff._get_model_for_agent = Codebuff._get_model_for_agent.__get__(codebuff, Codebuff)
        
        model = codebuff._get_model_for_agent("thinker")
        assert model == "gpt-4o"

    @pytest.mark.unit
    def test_get_model_for_agent_ultimate_fallback(self):
        """Test getting model with ultimate fallback."""
        from codebuff.main import Codebuff
        
        config = {}  # Empty config
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = config
        codebuff._get_model_for_agent = Codebuff._get_model_for_agent.__get__(codebuff, Codebuff)
        
        # Test specific fallbacks
        assert codebuff._get_model_for_agent("file_explorer") == "openai/gpt-4o-mini"
        assert codebuff._get_model_for_agent("thinker") == "openai/gpt-4o"
        assert codebuff._get_model_for_agent("unknown_agent") == "openai/gpt-4o"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_llm_for_agent_openrouter_preferred(self):
        """Test LLM creation with OpenRouter preference."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff._get_model_for_agent = MagicMock(return_value="openai/gpt-4o")
        
        # Mock the utility functions
        with patch('codebuff.main.get_llm_credentials') as mock_get_creds, \
             patch('codebuff.main.create_llm_model') as mock_create_model:
            
            mock_creds = MagicMock()
            mock_get_creds.return_value = mock_creds
            mock_model = MagicMock()
            mock_create_model.return_value = mock_model
            
            codebuff._get_llm_for_agent = Codebuff._get_llm_for_agent.__get__(codebuff, Codebuff)
            
            result = await codebuff._get_llm_for_agent(
                "thinker", 
                open_router_api_key=MagicMock(),  # Available
                openai_api_key=MagicMock()
            )
            
            assert result == mock_model
            mock_get_creds.assert_called_once_with("openrouter", mock.ANY, mock.ANY)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_llm_for_agent_openai_fallback(self):
        """Test LLM creation with OpenAI fallback."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff._get_model_for_agent = MagicMock(return_value="openai/gpt-4o")
        
        with patch('codebuff.main.get_llm_credentials') as mock_get_creds, \
             patch('codebuff.main.create_llm_model') as mock_create_model:
            
            mock_creds = MagicMock()
            mock_get_creds.return_value = mock_creds
            mock_model = MagicMock()
            mock_create_model.return_value = mock_model
            
            codebuff._get_llm_for_agent = Codebuff._get_llm_for_agent.__get__(codebuff, Codebuff)
            
            result = await codebuff._get_llm_for_agent(
                "thinker", 
                open_router_api_key=None,  # Not available
                openai_api_key=MagicMock()
            )
            
            assert result == mock_model
            mock_get_creds.assert_called_once_with("openai", None, mock.ANY)


class TestCodebuffAgentMethods:
    """Test individual Codebuff agent methods."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_explore_files_success(self):
        """Test successful file exploration."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = {"test": "config"}
        codebuff._get_llm_for_agent = AsyncMock(return_value=MagicMock())
        
        # Mock the agent
        with patch('codebuff.main.create_file_explorer_agent') as mock_create_agent:
            mock_agent = AsyncMock()
            mock_result = MagicMock()
            mock_result.output = "File exploration results"
            mock_agent.run = AsyncMock(return_value=mock_result)
            mock_create_agent.return_value = mock_agent
            
            codebuff.explore_files = Codebuff.explore_files.__get__(codebuff, Codebuff)
            
            result = await codebuff.explore_files(
                focus_area="test area",
                container=MagicMock(),
                openai_api_key=MagicMock()
            )
            
            assert result == "File exploration results"
            mock_agent.run.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_explore_files_no_api_key(self):
        """Test file exploration without API key."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.explore_files = Codebuff.explore_files.__get__(codebuff, Codebuff)
        
        result = await codebuff.explore_files(
            focus_area="test area",
            container=MagicMock(),
            openai_api_key=None,
            open_router_api_key=None
        )
        
        assert result == "Error: No API key provided"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_pick_files_success(self):
        """Test successful file picking."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = {"test": "config"}
        codebuff._get_llm_for_agent = AsyncMock(return_value=MagicMock())
        
        with patch('codebuff.main.create_file_picker_agent') as mock_create_agent:
            mock_agent = AsyncMock()
            mock_result = MagicMock()
            mock_result.output = "Selected files: file1.py, file2.py"
            mock_agent.run = AsyncMock(return_value=mock_result)
            mock_create_agent.return_value = mock_agent
            
            codebuff.pick_files = Codebuff.pick_files.__get__(codebuff, Codebuff)
            
            result = await codebuff.pick_files(
                task_description="test task",
                container=MagicMock(),
                openai_api_key=MagicMock()
            )
            
            assert "Selected files: file1.py, file2.py" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_plan_success(self):
        """Test successful plan creation."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = {"test": "config"}
        codebuff._get_llm_for_agent = AsyncMock(return_value=MagicMock())
        
        with patch('agents.codebuff.src.codebuff.main.create_thinker_agent') as mock_create_agent:
            mock_agent = AsyncMock()
            mock_result = MagicMock()
            mock_result.output = "Detailed implementation plan"
            mock_agent.run = AsyncMock(return_value=mock_result)
            mock_create_agent.return_value = mock_agent
            
            codebuff.create_plan = Codebuff.create_plan.__get__(codebuff, Codebuff)
            
            result = await codebuff.create_plan(
                task_description="implement feature",
                relevant_files="file1.py,file2.py",
                exploration_results="exploration data",
                container=MagicMock(),
                openai_api_key=MagicMock()
            )
            
            assert result == "Detailed implementation plan"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_implement_plan_success(self):
        """Test successful plan implementation."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = {"test": "config"}
        codebuff._get_llm_for_agent = AsyncMock(return_value=MagicMock())
        
        with patch('agents.codebuff.src.codebuff.main.create_implementation_agent') as mock_create_agent:
            mock_agent = AsyncMock()
            mock_result = MagicMock()
            mock_result.output = "Implementation completed successfully"
            mock_agent.run = AsyncMock(return_value=mock_result)
            mock_create_agent.return_value = mock_agent
            
            codebuff.implement_plan = Codebuff.implement_plan.__get__(codebuff, Codebuff)
            
            result = await codebuff.implement_plan(
                plan="detailed plan",
                container=MagicMock(),
                openai_api_key=MagicMock()
            )
            
            assert result == "Implementation completed successfully"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_review_changes_success(self):
        """Test successful change review."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = {"test": "config"}
        codebuff._get_llm_for_agent = AsyncMock(return_value=MagicMock())
        
        with patch('agents.codebuff.src.codebuff.main.create_reviewer_agent') as mock_create_agent:
            mock_agent = AsyncMock()
            mock_result = MagicMock()
            mock_result.output = "Review completed: Changes look good"
            mock_agent.run = AsyncMock(return_value=mock_result)
            mock_create_agent.return_value = mock_agent
            
            codebuff.review_changes = Codebuff.review_changes.__get__(codebuff, Codebuff)
            
            result = await codebuff.review_changes(
                changes_description="added new feature",
                container=MagicMock(),
                openai_api_key=MagicMock()
            )
            
            assert result == "Review completed: Changes look good"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_prune_context_success(self):
        """Test successful context pruning."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = {"test": "config"}
        codebuff._get_llm_for_agent = AsyncMock(return_value=MagicMock())
        
        with patch('agents.codebuff.src.codebuff.main.create_context_pruner_agent') as mock_create_agent:
            mock_agent = AsyncMock()
            mock_result = MagicMock()
            mock_result.output = "Context pruned successfully"
            mock_agent.run = AsyncMock(return_value=mock_result)
            mock_create_agent.return_value = mock_agent
            
            codebuff.prune_context = Codebuff.prune_context.__get__(codebuff, Codebuff)
            
            result = await codebuff.prune_context(
                max_tokens=1000,
                strategy="aggressive",
                container=MagicMock(),
                openai_api_key=MagicMock()
            )
            
            assert result == "Context pruned successfully"


class TestCodebuffPullRequestIntegration:
    """Test Codebuff pull request integration."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('codebuff.main.dag')
    async def test_create_pull_request_success(self, mock_dag):
        """Test successful pull request creation."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = {"test": "config"}
        codebuff.config_file = MagicMock()
        codebuff.github_token = MagicMock()
        
        # Mock get_llm_credentials
        with patch('agents.codebuff.src.codebuff.main.get_llm_credentials') as mock_get_creds:
            mock_creds = MagicMock()
            mock_get_creds.return_value = mock_creds
            
            # Mock PR agent and builder
            mock_pr_agent = AsyncMock()
            mock_builder = AsyncMock()
            mock_auth_container = AsyncMock()
            mock_result_container = AsyncMock()
            
            # Mock successful status
            mock_status_file = AsyncMock()
            mock_status_file.contents = AsyncMock(return_value="success")
            mock_result_container.file.return_value = mock_status_file
            
            mock_builder.setup_pull_request_container = AsyncMock(return_value=mock_auth_container)
            mock_pr_agent.run = AsyncMock(return_value=mock_result_container)
            
            mock_dag.pull_request_agent.return_value = mock_pr_agent
            mock_dag.builder.return_value = mock_builder
            
            codebuff.create_pull_request = Codebuff.create_pull_request.__get__(codebuff, Codebuff)
            
            result = await codebuff.create_pull_request(
                container=MagicMock(),
                task_description="test task",
                changes_description="test changes",
                openai_api_key=MagicMock()
            )
            
            assert "Pull request created successfully" in result
            mock_pr_agent.run.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('codebuff.main.dag')
    async def test_create_pull_request_failure(self, mock_dag):
        """Test pull request creation failure."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = {"test": "config"}
        codebuff.config_file = MagicMock()
        codebuff.github_token = MagicMock()
        
        with patch('agents.codebuff.src.codebuff.main.get_llm_credentials') as mock_get_creds:
            mock_creds = MagicMock()
            mock_get_creds.return_value = mock_creds
            
            # Mock failing PR agent
            mock_pr_agent = AsyncMock()
            mock_builder = AsyncMock()
            mock_auth_container = AsyncMock()
            mock_result_container = AsyncMock()
            
            # Mock failure status
            mock_status_file = AsyncMock()
            mock_status_file.contents = AsyncMock(return_value="failure")
            mock_error_file = AsyncMock()
            mock_error_file.contents = AsyncMock(return_value="PR creation failed")
            
            mock_result_container.file = MagicMock(side_effect=[
                mock_status_file,  # First call for status
                mock_error_file    # Second call for error
            ])
            
            mock_builder.setup_pull_request_container = AsyncMock(return_value=mock_auth_container)
            mock_pr_agent.run = AsyncMock(return_value=mock_result_container)
            
            mock_dag.pull_request_agent.return_value = mock_pr_agent
            mock_dag.builder.return_value = mock_builder
            
            codebuff.create_pull_request = Codebuff.create_pull_request.__get__(codebuff, Codebuff)
            
            result = await codebuff.create_pull_request(
                container=MagicMock(),
                task_description="test task",
                changes_description="test changes",
                openai_api_key=MagicMock()
            )
            
            assert "Pull request creation failed" in result


class TestCodebuffOrchestration:
    """Test Codebuff orchestration workflow."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    @patch('codebuff.main.dag')
    async def test_setup_environment_success(self, mock_dag):
        """Test successful environment setup."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = {
            "container": {
                "docker_file_path": "./Dockerfile"
            }
        }
        codebuff.config_file = MagicMock()
        
        # Mock git and builder
        mock_git = AsyncMock()
        mock_tree = AsyncMock()
        mock_branch = AsyncMock()
        mock_branch.tree = AsyncMock(return_value=mock_tree)
        mock_git.with_auth_token = AsyncMock(return_value=mock_git)
        mock_git.branch = AsyncMock(return_value=mock_branch)
        
        mock_builder = AsyncMock()
        mock_container = AsyncMock()
        mock_builder.build_test_environment = AsyncMock(return_value=mock_container)
        
        mock_dag.git.return_value = mock_git
        mock_dag.builder.return_value = mock_builder
        
        codebuff.setup_environment = Codebuff.setup_environment.__get__(codebuff, Codebuff)
        
        result = await codebuff.setup_environment(
            github_access_token=MagicMock(),
            repository_url="https://github.com/test/repo",
            branch="main",
            openai_api_key=MagicMock()
        )
        
        assert result == mock_container
        mock_builder.build_test_environment.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.asyncio
    @patch('codebuff.main.dag')
    async def test_orchestrate_feature_development_workflow(self, mock_dag):
        """Test complete feature development orchestration."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = {"test": "config"}
        codebuff.github_token = None
        codebuff.container = None
        codebuff._get_llm_for_agent = AsyncMock(return_value=MagicMock())
        
        # Mock setup_environment to set container
        async def mock_setup_env(*args, **kwargs):
            codebuff.container = MagicMock()
            codebuff.github_token = MagicMock()
            return codebuff.container
        
        codebuff.setup_environment = AsyncMock(side_effect=mock_setup_env)
        
        # Mock orchestrator agent
        with patch('agents.codebuff.src.codebuff.main.create_orchestrator_agent') as mock_create_agent:
            mock_agent = AsyncMock()
            mock_result = MagicMock()
            mock_result.output = "Workflow completed successfully"
            mock_agent.run = AsyncMock(return_value=mock_result)
            mock_create_agent.return_value = mock_agent
            
            codebuff.orchestrate_feature_development = Codebuff.orchestrate_feature_development.__get__(codebuff, Codebuff)
            
            result = await codebuff.orchestrate_feature_development(
                github_token=MagicMock(),
                task_description="implement new feature",
                repo_url="https://github.com/test/repo",
                openai_api_key=MagicMock()
            )
            
            assert "Workflow completed successfully" in result
            codebuff.setup_environment.assert_called_once()
            mock_agent.run.assert_called()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_orchestrate_feature_development_no_api_key(self):
        """Test orchestration without API key."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.orchestrate_feature_development = Codebuff.orchestrate_feature_development.__get__(codebuff, Codebuff)
        
        result = await codebuff.orchestrate_feature_development(
            github_token=MagicMock(),
            task_description="test task",
            repo_url="https://github.com/test/repo",
            openai_api_key=None,
            open_router_api_key=None
        )
        
        assert "Error: No API key provided" in result


class TestCodebuffErrorHandling:
    """Test Codebuff error handling scenarios."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_explore_files_exception_handling(self):
        """Test file exploration with exception."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = {"test": "config"}
        codebuff._get_llm_for_agent = AsyncMock(side_effect=Exception("LLM creation failed"))
        
        codebuff.explore_files = Codebuff.explore_files.__get__(codebuff, Codebuff)
        
        result = await codebuff.explore_files(
            focus_area="test area",
            container=MagicMock(),
            openai_api_key=MagicMock()
        )
        
        assert "Error exploring files: LLM creation failed" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_pick_files_exception_handling(self):
        """Test file picking with exception."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.config = {"test": "config"}
        codebuff._get_llm_for_agent = AsyncMock(return_value=MagicMock())
        
        with patch('codebuff.main.create_file_picker_agent') as mock_create_agent:
            mock_create_agent.side_effect = Exception("Agent creation failed")
            
            codebuff.pick_files = Codebuff.pick_files.__get__(codebuff, Codebuff)
            
            result = await codebuff.pick_files(
                task_description="test task",
                container=MagicMock(),
                openai_api_key=MagicMock()
            )
            
            assert "Error picking files: Agent creation failed" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_orchestrate_workflow_exception_handling(self):
        """Test orchestration workflow with exception."""
        from codebuff.main import Codebuff
        
        codebuff = MagicMock(spec=Codebuff)
        codebuff.github_token = None
        codebuff.setup_environment = AsyncMock(side_effect=Exception("Setup failed"))
        
        codebuff.orchestrate_feature_development = Codebuff.orchestrate_feature_development.__get__(codebuff, Codebuff)
        
        result = await codebuff.orchestrate_feature_development(
            github_token=MagicMock(),
            task_description="test task",
            repo_url="https://github.com/test/repo",
            openai_api_key=MagicMock()
        )
        
        assert "Error in orchestrated workflow: Setup failed" in result