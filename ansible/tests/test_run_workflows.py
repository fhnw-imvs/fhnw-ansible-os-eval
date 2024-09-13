import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import sys

sys.path.insert(0, '../ansible/roles/evaluation-tool/module_utils')

from run_workflows import run_workflows


@pytest.fixture
def selected_llm_config():
    return {
        "model": "gpt-3.5-turbo",
        "api_key": "test_api_key",
    }


@pytest.fixture
def selected_key():
    return "gpt"


@pytest.fixture
def categories():
    return [
        {
            "category_id": "Security",
            "topics": [
                {
                    "identifier": "ssh_config",
                    "command_outputs": {"ssh -V": "OpenSSH_7.6p1, OpenSSL 1.0.2n  7 Dec 2017"},
                    "file_contents": {
                        "/etc/ssh/sshd_config": "PermitRootLogin yes\nPasswordAuthentication yes\n"
                    },
                    "service_infos": {}
                }
            ]
        }
    ]


@pytest.fixture
def node_name():
    return "node-1"


@patch('run_workflows.create_chat_model_from_config')
@patch('run_workflows.RequestScheduler')
@patch('run_workflows.Workflow')
@pytest.mark.asyncio
async def test_run_workflows(mock_Workflow, mock_RequestScheduler, mock_create_chat_model_from_config, selected_llm_config, selected_key, categories, node_name):
    mock_model = AsyncMock()
    mock_create_chat_model_from_config.return_value = mock_model

    mock_scheduler_instance = AsyncMock()
    mock_RequestScheduler.return_value = mock_scheduler_instance

    mock_workflow_instance = AsyncMock()
    mock_Workflow.return_value = mock_workflow_instance

    mock_model.ainvoke.return_value = {"success": True}  # Example of a successful response

    mock_scheduler_instance.schedule_workflow.return_value = "Workflow result"

    report = await run_workflows(selected_llm_config, selected_key, categories, node_name)

    mock_create_chat_model_from_config.assert_called_once_with(selected_llm_config, selected_key)
    mock_RequestScheduler.assert_called_once()
    mock_Workflow.assert_called_once_with(mock_model, "Security", categories[0]['topics'][0])
    mock_scheduler_instance.schedule_workflow.assert_awaited_once_with(mock_workflow_instance)

    expected_report = (
        f"# Final report for node: {node_name}\n"
        f"## Category: Security\n"
        "Workflow result"
    )

    assert report == expected_report
