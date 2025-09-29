"""Critical path smoke tests for orchestrator workflow functions."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime


class TestOrchestratorCriticalPaths:
    """Test critical orchestrator workflow functions for basic functionality."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_start_task_smoke(self):
        """Smoke test for start_task function."""
        from codebuff.orchestrator.agent import start_task
        from codebuff.orchestrator.models import OrchestratorDependencies, OrchestrationState, TaskSpec, Phase, Status
        
        # Mock dependencies
        mock_container = MagicMock()
        mock_container.with_new_file = MagicMock(return_value=mock_container)
        
        deps = OrchestratorDependencies(
            config=MagicMock(),
            container=mock_container,
            config_file=MagicMock(),
            api_key=MagicMock(),
            state=None
        )
        
        ctx = MagicMock()
        ctx.deps = deps
        
        # Test start_task creates initial state
        result = await start_task(ctx, "test task", "test focus")
        
        assert "started" in result
        assert deps.state is not None
        assert deps.state.task_spec.goal == "test task"
        assert deps.state.current_phase == Phase.EXPLORATION

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_implementation_plan_smoke(self):
        """Smoke test for create_implementation_plan function."""
        from codebuff.orchestrator.agent import create_implementation_plan
        from codebuff.orchestrator.models import OrchestratorDependencies, OrchestrationState, TaskSpec, Phase, Status
        
        # Mock container and write operations
        mock_container = MagicMock()
        mock_container.with_new_file = MagicMock(return_value=mock_container)
        
        with patch('codebuff.orchestrator.agent.write_text') as mock_write_text:
            mock_write_text.return_value = mock_container
            
            deps = OrchestratorDependencies(
                config=MagicMock(),
                container=mock_container,
                config_file=MagicMock(),
                api_key=MagicMock(),
                state=OrchestrationState(
                    task_id="test-123",
                    current_phase=Phase.PLANNING,
                    status=Status.IN_PROGRESS,
                    start_time=datetime.now(),
                    last_update=datetime.now(),
                    task_spec=TaskSpec(id="test", goal="test goal", focus_area="test")
                )
            )
            
            ctx = MagicMock()
            ctx.deps = deps
            
            result = await create_implementation_plan(ctx)
            
            assert "Implementation plan created" in result
            assert deps.state.plan is not None
            assert len(deps.state.plan.steps) >= 4
            mock_write_text.assert_called()

    @pytest.mark.unit
    @pytest.mark.asyncio 
    async def test_orchestrator_tools_planning_smoke(self):
        """Smoke test for orchestrator planning tools."""
        from codebuff.orchestrator.tools.planning import create_plan, add_subgoal
        from codebuff.orchestrator.models import OrchestratorDependencies
        
        mock_container = MagicMock()
        mock_container.with_new_file = MagicMock(return_value=mock_container)
        
        with patch('codebuff.orchestrator.tools.planning.write_text') as mock_write_text, \
             patch('codebuff.orchestrator.tools.planning.append_log') as mock_append_log:
            
            mock_write_text.return_value = mock_container
            mock_append_log.return_value = mock_container
            
            deps = OrchestratorDependencies(
                config=MagicMock(),
                container=mock_container,
                config_file=MagicMock(),
                api_key=MagicMock()
            )
            
            ctx = MagicMock()
            ctx.deps = deps
            
            # Test create_plan
            result = await create_plan(ctx, "test.md", "# Test Plan\nStep 1: Do something")
            assert "Plan written" in result
            mock_write_text.assert_called_with(mock_container, "plans/test.md", "# Test Plan\nStep 1: Do something")
            
            # Test add_subgoal
            result = await add_subgoal(ctx, "1", "Test objective", "IN_PROGRESS")
            assert "Subgoal added" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_orchestrator_tools_file_ops_smoke(self):
        """Smoke test for orchestrator file operations tools."""
        from codebuff.orchestrator.tools.file_ops import read_files, write_file, str_replace
        from codebuff.orchestrator.models import OrchestratorDependencies
        
        mock_container = MagicMock()
        mock_file = MagicMock()
        mock_file.contents = AsyncMock(return_value="test content")
        mock_container.file = MagicMock(return_value=mock_file)
        mock_container.with_new_file = MagicMock(return_value=mock_container)
        
        deps = OrchestratorDependencies(
            config=MagicMock(),
            container=mock_container,
            config_file=MagicMock(),
            api_key=MagicMock()
        )
        
        ctx = MagicMock()
        ctx.deps = deps
        
        # Test read_files
        result = await read_files(ctx, ["test.py"])
        data = json.loads(result)
        assert len(data) == 1
        assert data[0]["path"] == "test.py"
        assert data[0]["content"] == "test content"
        
        # Test write_file
        result = await write_file(ctx, "test.py", "test instructions", "new content")
        assert "Wrote: test.py" in result
        mock_container.with_new_file.assert_called_with("test.py", "new content")
        
        # Test str_replace
        result = await str_replace(ctx, "test.py", [{"old": "test", "new": "new"}])
        assert "Replaced in: test.py" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_orchestrator_tools_sub_agents_smoke(self):
        """Smoke test for orchestrator sub-agent wrapper tools."""
        from codebuff.orchestrator.tools.sub_agents import run_file_explorer, run_file_picker
        from codebuff.orchestrator.models import OrchestratorDependencies
        
        mock_container = MagicMock()
        
        deps = OrchestratorDependencies(
            config=MagicMock(),
            container=mock_container,
            config_file=MagicMock(),
            api_key=MagicMock()
        )
        
        ctx = MagicMock()
        ctx.deps = deps
        
        with patch('yaml.safe_dump') as mock_yaml, \
             patch('codebuff.orchestrator.tools.sub_agents.dag') as mock_dag:
            
            mock_yaml.return_value = "config: test"
            mock_code_map = AsyncMock()
            mock_code_map.get_file_token_scores = AsyncMock(return_value='{"fileTokenScores": {"test.py": {"test": 1}}}')
            mock_dag.directory().with_new_file().file.return_value = MagicMock()
            mock_dag.code_map.return_value = mock_code_map
            
            # Test run_file_explorer
            result = await run_file_explorer(ctx, "test focus")
            assert isinstance(result, str)
            data = json.loads(result)
            assert "focus_area" in data
            assert data["focus_area"] == "test focus"
            
            # Test run_file_picker  
            result = await run_file_picker(ctx, "find auth files")
            assert isinstance(result, str)
            # Should be JSON array of ranked files
            files_data = json.loads(result)
            assert isinstance(files_data, list)
