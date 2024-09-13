import asyncio

from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.run_workflows import run_workflows


def main():
    module_args = dict(
        llm_name=dict(type='str', required=True),
        llm_config=dict(type='dict', required=True),
        categories=dict(type='list', elements='dict', required=True),
        node_name=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    selected_key = module.params['llm_name']
    selected_llm_config = module.params['llm_config'][selected_key.split("-")[0]]
    categories = module.params['categories']
    node_name = module.params['node_name']

    # value = create_chat_model_from_config(selected_llm_config, selected_key)
    report = asyncio.run(run_workflows(selected_llm_config, selected_key, categories, node_name))

    result = dict(
        change=False,
        message="Module completed successfully",
        report=report
    )
    module.exit_json(**result)


if __name__ == '__main__':
    main()