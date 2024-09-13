import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys

sys.path.insert(0, '../ansible/roles/evaluation-tool/module_utils')

from RequestScheduler import RequestScheduler
from Workflow import Workflow
from langchain_ollama import ChatOllama


@pytest.fixture
def scheduler():
    return RequestScheduler()


@pytest.fixture
def workflow():
    wf = MagicMock(spec=Workflow)
    wf.model = MagicMock()
    return wf


@pytest.mark.asyncio
async def test_schedule_workflow_with_ollama(scheduler, workflow):
    workflow.model = MagicMock(spec=ChatOllama)
    workflow.ainvoke = AsyncMock(return_value="ollama_success")

    result = await scheduler.schedule_workflow(workflow)

    workflow.ainvoke.assert_called_once()
    assert result == "ollama_success"


@pytest.mark.asyncio
@patch.object(RequestScheduler, 'can_make_request', new_callable=AsyncMock)
@patch.object(RequestScheduler, 'update_rate_limits', new_callable=MagicMock)
async def test_schedule_workflow_with_non_ollama(mock_update_rate_limits, mock_can_make_request, scheduler, workflow):
    mock_can_make_request.return_value = True
    workflow.ainvoke = AsyncMock(return_value="success")

    result = await scheduler.schedule_workflow(workflow)

    workflow.ainvoke.assert_called_once()
    mock_update_rate_limits.assert_called_once_with(workflow.model)
    assert result == "success"

@pytest.mark.asyncio
@patch.object(RequestScheduler, 'can_make_request', new_callable=AsyncMock)
async def test_schedule_workflow_with_rate_limit(mock_can_make_request, scheduler, workflow):
    mock_can_make_request.return_value = False
    workflow.ainvoke = AsyncMock()

    scheduler.schedule_workflow_for_online = AsyncMock(return_value="scheduled_later")
    result = await scheduler.schedule_workflow(workflow)

    workflow.ainvoke.assert_not_called()
    scheduler.schedule_workflow_for_online.assert_called_once_with(workflow)
    assert result == "scheduled_later"

@pytest.mark.asyncio
async def test_can_make_request_with_no_rate_limit(scheduler, workflow):
    result = await scheduler.can_make_request(workflow.model)
    assert result


@pytest.mark.asyncio
async def test_can_make_request_with_retry_after(scheduler, workflow, mocker):
    scheduler.first_load = False  # Ensure that first_load is False to process headers
    workflow.model.get_response_headers.return_value = [{"retry-after": "2"}]

    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        result = await scheduler.can_make_request(workflow.model)

        mock_sleep.assert_called_once_with(2.0)
        assert not result


@pytest.mark.asyncio
async def test_update_rate_limits_with_headers(scheduler, workflow):
    headers = {
        "x-ratelimit-remaining-requests": "100",
        "x-ratelimit-remaining-tokens": "4000"
    }
    scheduler.first_load = False  # Ensure it's not the first load
    workflow.model.get_response_headers.return_value = [headers]

    scheduler.update_rate_limits(workflow.model)

    assert scheduler.current_requests == 100
    assert scheduler.current_tokens == 4000

@pytest.mark.asyncio
async def test_update_rate_limits_first_load(scheduler, workflow):
    scheduler.first_load = True
    headers = {
        "x-ratelimit-remaining-requests": "120",
        "x-ratelimit-remaining-tokens": "7000"
    }
    workflow.model.get_response_headers.return_value = [headers]

    scheduler.update_rate_limits(workflow.model)

    assert scheduler.current_requests == 128  # Should remain as init_max_requests
    assert scheduler.current_tokens == 8192   # Should remain as init_max_tokens
    assert scheduler.first_load
