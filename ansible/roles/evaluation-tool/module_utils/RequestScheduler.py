try:
    from ansible.module_utils.Workflow import Workflow
except ImportError: # We except an ImportError in unit tests so we import it differently :D
    from Workflow import Workflow

from langchain_ollama import ChatOllama

import asyncio

class RequestScheduler:
    init_max_requests = 128     # not expected to have 128 concurrent requests until we get the first response
    init_max_tokens = 8192      # min token size of the supported llm
    prompt_length = 587         # lenght of the workflow prompt
    topic_data_min_length = 5   # min content size of configured topics

    def __init__(self):
        self.max_requests = self.init_max_requests
        self.max_tokens = self.init_max_tokens
        self.current_requests = self.init_max_requests
        self.current_tokens = self.init_max_tokens
        self.lock = asyncio.Lock()
        self.first_load = True

    async def schedule_workflow(self, workflow: Workflow):
        if isinstance(workflow.model, ChatOllama):
            return await workflow.ainvoke()
        elif await self.can_make_request(workflow.model):
            result = await workflow.ainvoke()
            self.update_rate_limits(workflow.model)
            return result
        else:
            return await self.schedule_workflow_for_online(workflow)

    async def can_make_request(self, model):
        headers = model.get_response_headers()[-1] if not self.first_load else {}

        retry_after = headers.get("retry-after")
        if retry_after:
            print(f"Rate limit exceeded, waiting for {retry_after} seconds.")
            await asyncio.sleep(float(retry_after))
            return False

        min_length = self.prompt_length + self.topic_data_min_length
        return self.current_requests > 0 and self.current_tokens > min_length

    def update_rate_limits(self, model):
        headers = model.get_response_headers()[-1] if not self.first_load else {}

        self.current_requests = int(headers.get("x-ratelimit-remaining-requests", self.init_max_requests))
        self.current_tokens = int(headers.get("x-ratelimit-remaining-tokens", self.init_max_tokens))
        self.first_load = True
