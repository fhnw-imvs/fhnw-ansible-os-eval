import json
from typing import List, Dict

from langgraph.graph import Graph

from langchain_core.prompts import PromptTemplate

from pydantic import BaseModel, Field, ValidationError

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import StructuredTool


class NonConformingIssue(BaseModel):
    issue: str
    fix: str


class EvaluationResult(BaseModel):
    is_conform: bool = Field(description="Indicates if the input conforms to best practices")
    non_conforming_issues: List[NonConformingIssue] = Field(default_factory=list)
    identifier: str = Field(default="", description="The identifier for the topic")


class CommandOutputsSchema(BaseModel):
    command_outputs: dict


class FileContentsSchema(BaseModel):
    file_contents: dict


class ServiceInfosSchema(BaseModel):
    service_infos: dict


class AggregationInputSchema(BaseModel):
    command_output_result: EvaluationResult
    file_contents_result: EvaluationResult
    service_infos_result: EvaluationResult


class TopicSchema(BaseModel):
    identifier: str
    command_outputs: dict
    file_contents: dict
    service_infos: dict


class RequestSchema(BaseModel):
    category_name: str
    topic: TopicSchema


class EvaluationOutput(BaseModel):
    result: EvaluationResult


class ResponseSchema(BaseModel):
    identifier: str
    is_conform: bool
    non_conforming_issues: List[NonConformingIssue]


# Define the state schema with annotated reducers
class StateSchema(BaseModel):
    instruction_data: dict = Field(default_factory=dict)
    command_output_result: EvaluationResult = Field(default_factory=lambda: EvaluationResult(is_conform=True, non_conforming_issues=[]))
    file_contents_result: EvaluationResult = Field(default_factory=lambda: EvaluationResult(is_conform=True, non_conforming_issues=[]))
    service_infos_result: EvaluationResult = Field(default_factory=lambda: EvaluationResult(is_conform=True, non_conforming_issues=[]))
    aggregate_result: dict = Field(default_factory=dict)
    formatted_result: str = ""


class Workflow:
    def __init__(self, model, category_name, topic: Dict):
        self.model = model
        self.category_name = category_name
        self.topic = TopicSchema(**topic)  # Parse the topic dictionary into a TopicSchema object
        self.identifier = self.topic.identifier
        self.graph = self.create_graph()
        self.command_outputs_template = PromptTemplate.from_template("""
        You are an IT expert specializing in best practices. Evaluate the command outputs for the category "{category_name}". Identify if they conform to best practices. Do not validate the command itself, as they may not be conforming.

        **Command Outputs:**
        {command_outputs}

        **Result Format:**

        - If the command outputs conform to best practices:
          is_conform: true
          non_conforming_issues: []

        - If not:
          is_conform: false
          non_conforming_issues:
            - issue: "issue_text"
              fix: "fix_text"
        """)

        self.file_contents_template = PromptTemplate.from_template("""
        You are an IT expert specializing in best practices. Evaluate the file contents for the category "{category_name}". Identify if they conform to best practices. Try to find all flaws in the file.

        **File Contents:**
        {file_contents}

        **Result Format:**

        - If the file contents conform to best practices:
          is_conform: true
          non_conforming_issues: []

        - If not:
          is_conform: false
          non_conforming_issues:
            - issue: "issue_text"
              fix: "fix_text"
        """)

        self.service_infos_template = PromptTemplate.from_template("""
        You are an IT expert specializing in best practices. Evaluate the service information for the category "{category_name}". Identify if it conforms to best practices.

        **Service Information:**
        {service_infos}

        **Result Format:**

        - If the service information conforms to best practices:
          is_conform: true
          non_conforming_issues: []

        - If not:
          is_conform: false
          non_conforming_issues:
            - issue: "issue_text"
              fix: "fix_text"
        """)

    def instruction_agent(self, **kwargs):
        try:
            request_data = RequestSchema(**kwargs)
            instruction_data = request_data.dict()
            return {"instruction_data": instruction_data}
        except ValidationError as e:
            raise ValueError(f"Invalid request structure: {e}")

    async def evaluate_command_outputs(self, **state):
        command_outputs = state.get("instruction_data", {}).get("topic", {}).get("command_outputs", {})
        result = EvaluationResult(is_conform=True, non_conforming_issues=[], identifier=self.identifier)

        if command_outputs:
            command_outputs_json = json.dumps(command_outputs, indent=2)
            query = self.command_outputs_template.format(
                category_name=self.category_name,
                command_outputs=command_outputs_json
            )

            try:
                model_response = await self.model.with_structured_output(schema=EvaluationOutput).ainvoke(query)
                result = model_response.result
                result.identifier = self.identifier
            except Exception as e:
                result = EvaluationResult(
                    is_conform=False,
                    non_conforming_issues=[NonConformingIssue(
                        issue=f"Failed to evaluate command outputs because of {e}",
                        fix="Check model invocation for command outputs."
                    )],
                    identifier=self.identifier
                )

        state["command_output_result"] = result
        return state

    async def evaluate_file_contents(self, **state):
        file_contents = state.get("instruction_data", {}).get("topic", {}).get("file_contents", {})
        result = EvaluationResult(is_conform=True, non_conforming_issues=[], identifier=self.identifier)

        if file_contents:
            file_contents_json = json.dumps(file_contents, indent=2)
            query = self.file_contents_template.format(
                category_name=self.category_name,
                file_contents=file_contents_json
            )

            try:
                model_response = await self.model.with_structured_output(schema=EvaluationOutput).ainvoke(query)
                result = model_response.result
                result.identifier = self.identifier
            except Exception as e:
                result = EvaluationResult(
                    is_conform=False,
                    non_conforming_issues=[NonConformingIssue(
                        issue=f"Failed to evaluate file contents because of {e}",
                        fix="Check model invocation for file contents."
                    )],
                    identifier=self.identifier
                )

        state["file_contents_result"] = result
        return state

    async def evaluate_service_infos(self, **state):
        service_infos = state.get("instruction_data", {}).get("topic", {}).get("service_infos", {})
        result = EvaluationResult(is_conform=True, non_conforming_issues=[], identifier=self.identifier)

        if service_infos:
            service_infos_json = json.dumps(service_infos, indent=2)
            query = self.service_infos_template.format(
                category_name=self.category_name,
                service_infos=service_infos_json
            )

            try:
                model_response = await self.model.with_structured_output(schema=EvaluationOutput).ainvoke(query)
                result = model_response.result
                result.identifier = self.identifier
            except Exception as e:
                result = EvaluationResult(
                    is_conform=False,
                    non_conforming_issues=[NonConformingIssue(
                        issue=f"Failed to evaluate service information because of {e}",
                        fix="Check model invocation for service information."
                    )],
                    identifier=self.identifier
                )

        print(f"Service Infos Evaluation Result: {result}")
        state["service_infos_result"] = result
        return state

    async def aggregate_results(self, **state):
        # Initialize default results in case of missing inputs
        command_output_result = state.get("command_output_result", EvaluationResult(is_conform=True, non_conforming_issues=[]))
        file_contents_result = state.get("file_contents_result", EvaluationResult(is_conform=True, non_conforming_issues=[]))
        service_infos_result = state.get("service_infos_result", EvaluationResult(is_conform=True, non_conforming_issues=[]))

        # Aggregate results
        is_conform = command_output_result.is_conform and file_contents_result.is_conform and service_infos_result.is_conform
        non_conforming_issues = (
            command_output_result.non_conforming_issues +
            file_contents_result.non_conforming_issues +
            service_infos_result.non_conforming_issues
        )

        # Use the identifier propagated from the evaluation results
        identifier = self.identifier

        response = {
            "identifier": identifier,
            "is_conform": is_conform,
            "non_conforming_issues": non_conforming_issues
        }
        state["aggregate_result"] = response
        return state

    def format_to_md(self, **state):
        response = state.get("aggregate_result", {})
        identifier = response.get("identifier", "Unknown")
        is_conform = response.get("is_conform", False)
        non_conforming_issues = response.get("non_conforming_issues", [])

        if is_conform:
            format_response = f"### {identifier}\n"
            format_response += f"#### Is conform: \"**yes**\"\n\n"

        elif not is_conform and non_conforming_issues:
            format_response = f"### {identifier}\n"
            format_response += f"#### Is conform: \"**no**\"\n\n"
            format_response += "#### Non-Conforming Issues:\n"
            for issue in non_conforming_issues:
                format_response += f"- Issue: {issue.issue}\n"
                format_response += f"- Fix: {issue.fix}\n"
            format_response += "\n"

        else:
            format_response = f"### {identifier}\n"
            format_response += f"#### Is conform: \"**unknown**\"\n\n"

        return format_response

    def create_graph(self):
        workflow = Graph()

        instruction_tool = StructuredTool.from_function(
            func=self.instruction_agent,
            args_schema=RequestSchema,
            name="InstructionAgent",
            description="Prepare and validate input"
        )

        command_output_tool = StructuredTool.from_function(
            coroutine=self.evaluate_command_outputs,
            args_schema=StateSchema,
            name="EvaluateCommandOutputsTool",
            description="Evaluate command outputs"
        )

        file_contents_tool = StructuredTool.from_function(
            coroutine=self.evaluate_file_contents,
            args_schema=StateSchema,
            name="EvaluateFileContentsTool",
            description="Evaluate file contents"
        )

        service_infos_tool = StructuredTool.from_function(
            coroutine=self.evaluate_service_infos,
            args_schema=StateSchema,
            name="EvaluateServiceInfosTool",
            description="Evaluate service information"
        )

        aggregation_tool = StructuredTool.from_function(
            coroutine=self.aggregate_results,
            args_schema=StateSchema,
            name="AggregateResultsTool",
            description="Aggregate evaluation results"
        )

        format_tool = StructuredTool.from_function(
            func=self.format_to_md,
            args_schema=StateSchema,
            name="FormatTool",
            description="Format evaluation results to markdown"
        )

        workflow.add_node("instruction_node", instruction_tool)
        workflow.add_node("command_output_node", command_output_tool)
        workflow.add_node("file_contents_node", file_contents_tool)
        workflow.add_node("service_infos_node", service_infos_tool)
        workflow.add_node("aggregate_node", aggregation_tool)
        workflow.add_node("format_node", format_tool)

        workflow.add_edge("instruction_node", "command_output_node")
        workflow.add_edge("command_output_node", "file_contents_node")
        workflow.add_edge("file_contents_node", "service_infos_node")
        workflow.add_edge("service_infos_node", "aggregate_node")
        workflow.add_edge("aggregate_node", "format_node")

        workflow.set_entry_point("instruction_node")
        workflow.set_finish_point("format_node")

        graph = workflow.compile()
        return graph

    def invoke(self):
        params = {
            "category_name": self.category_name,
            "topic": self.topic.dict()
        }
        return self.graph.invoke(params)

    async def ainvoke(self):
        params = {
            "category_name": self.category_name,
            "topic": self.topic.dict()
        }
        return await self.graph.ainvoke(params)
