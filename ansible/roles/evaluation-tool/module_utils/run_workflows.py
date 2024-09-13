try:
    from ansible.module_utils.RequestScheduler import RequestScheduler
    from ansible.module_utils.Workflow import Workflow
    from ansible.module_utils.create_model import create_chat_model_from_config
except ImportError:  # We except an ImportError in unit tests, so we import it differently
    from RequestScheduler import RequestScheduler
    from Workflow import Workflow
    from create_model import create_chat_model_from_config


async def verify_model_is_reachable(model):
    try:
        response = await model.ainvoke("Test connection")

        if response and 'error' not in response:
            return True
        else:
            raise ConnectionError(
                f"Service is reachable, but there might be an issue with the API key or response: {response}")

    except Exception as e:
        raise ConnectionError(f"Failed to verify model and service: {e}")


async def run_workflows(selected_llm_config, selected_key, categories, node_name):
    reports = [f"# Final report for node: {node_name}\n"]

    model = create_chat_model_from_config(selected_llm_config, selected_key)
    await verify_model_is_reachable(model)

    requests_scheduler = RequestScheduler()

    for category in categories:
        category_name = category['category_id']
        reports.append(f"## Category: {category_name}\n")

        for topic in category['topics']:
            workflow = Workflow(model, category_name, topic)
            result = await requests_scheduler.schedule_workflow(workflow)
            reports.append(result)

    return "".join(reports)
