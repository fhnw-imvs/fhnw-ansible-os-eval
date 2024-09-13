import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys

sys.path.insert(0, '../ansible/roles/evaluation-tool/module_utils')

from Workflow import Workflow, RequestSchema


@pytest.fixture
def category_name():
    return "Security"


@pytest.fixture
def topic():
    return {
        "identifier": "ssh_config",
        "command_outputs": {"ssh -V": "OpenSSH_7.6p1, OpenSSL 1.0.2n  7 Dec 2017"},
        "file_contents": {
            "/etc/ssh/sshd_config": "PermitRootLogin yes\nPasswordAuthentication yes\n"
        },
        "service_infos": {}
    }


@pytest.fixture
def workflow(category_name, topic):
    model = MagicMock()
    return Workflow(model, category_name, topic)


@patch('Workflow.json.dumps')
@patch('Workflow.RequestSchema')
def test_instruction_agent(MockRequestSchema, mock_json_dumps, workflow, category_name, topic):
    mock_json_dumps.side_effect = lambda x, **kwargs: x

    mock_request_instance = MagicMock()
    mock_request_instance.dict.return_value = {
        "category_name": category_name,
        "topic": {
            "identifier": topic["identifier"],
            "command_outputs": topic["command_outputs"],
            "file_contents": topic["file_contents"],
            "service_infos": topic["service_infos"]
        }
    }
    MockRequestSchema.return_value = mock_request_instance

    instruction_data = workflow.instruction_agent(category_name=category_name, topic=topic)

    expected_instruction_data = {
        "instruction_data": {
            "category_name": category_name,
            "topic": {
                "identifier": topic["identifier"],
                "command_outputs": topic["command_outputs"],
                "file_contents": topic["file_contents"],
                "service_infos": topic["service_infos"]
            }
        }
    }

    assert instruction_data == expected_instruction_data
    MockRequestSchema.assert_called_once()


@patch.object(Workflow, 'create_graph')
def test_invoke(mock_create_graph, workflow, category_name, topic):
    mock_graph = MagicMock()
    mock_create_graph.return_value = mock_graph

    workflow.graph = mock_graph
    workflow.invoke()
    mock_graph.invoke.assert_called_once_with({
        "category_name": category_name,
        "topic": topic
    })


@patch.object(Workflow, 'create_graph')
@pytest.mark.asyncio
async def test_ainvoke(mock_create_graph, workflow, category_name, topic):
    mock_graph = AsyncMock()
    mock_create_graph.return_value = mock_graph

    workflow.graph = mock_graph
    await workflow.ainvoke()
    mock_graph.ainvoke.assert_called_once_with({
        "category_name": category_name,
        "topic": topic
    })
