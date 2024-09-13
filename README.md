# AI-Based Operating System Evaluation
This project automates the process of gathering information from managed nodes, evaluating best practices using language models (LLMs), and generating comprehensive reports. The system is designed to facilitate compliance checks and recommend improvements by leveraging advanced AI workflows. The project is structured in two main phases: data gathering and AI-driven evaluation. It utilizes Ansible for automation, ensuring efficient and scalable operations across diverse environments. Key features include dynamic configuration, seamless integration with various LLMs, and humanreadable final reports.

The code is in the directory `./ansible`
## Supported models
For the online LLMs, we included the following two models:
![supported_models.png](images/supported_models.png)

For offline use, we support Llama 3.1 too running on Ollama. 
## Final evaluation report
The final report looks like this:
```markdown 
# Report for node01
## Category: security
### ssh config: no
  - Issue: Port 22 is not explicitly set, it's best to set this explicitly.
  - Fix: Uncomment and set the Port to 22.

  - Issue: PermitRootLogin is not set, it's recommended to set this to no to prevent root logins.
  - Fix: Set PermitRootLogin to no.

  - Issue: PasswordAuthentication is set to no, it's recommended to set this to yes for a more secure configuration.
  - Fix: Set PasswordAuthentication to yes.
### ssh key permissions: yes
...
```

## Documentation for initial setup and how to use
- [Ansible](ansible/README.md#ansible)
   * [Setup](ansible/README.md#setup)
      + [Add correct user to ansible.cfg](ansible/README.md#add-correct-user-to-ansiblecfg)
      + [Add clouds.yml file](ansible/README.md#add-cloudsyml-file)
      + [Setup python virtual environment and required python packages](ansible/README.md#setup-python-virtual-environment-and-required-python-packages)
      + [LLM config](ansible/README.md#llm-config)
      + [How to install Ollama](ansible/README.md#how-to-install-ollama)
   * [How to run](ansible/README.md#how-to-run)
      + [In the ansible/ directory of this repository](ansible/README.md#in-the-ansible-directory-of-this-repository)
         - [Run playbook with default LLM (=gpt)](ansible/README.md#run-playbook-with-default-llm-gpt)
         - [Run playbook with selected LLM (take a look at the LLM configuration file)](ansible/README.md#run-playbook-with-selected-llm-take-a-look-at-the-llm-configuration-file)
         - [Turn of information processing from the managed nodes to only run AI Requests](ansible/README.md#turn-of-information-processing-from-the-managed-nodes-to-only-run-ai-requests)
         - [Turn of AI Requests and only process the information on the managed nodes](ansible/README.md#turn-of-ai-requests-and-only-process-the-information-on-the-managed-nodes)
   * [How to use in other repos](ansible/README.md#how-to-use-in-other-repos)
      + [Add to another file in this repo](ansible/README.md#add-to-another-file-in-this-repo)
      + [As a role for another file/ project](ansible/README.md#as-a-role-for-another-file-project)


## Documentation for evaluation-tool role:
- [evaluation-tool](ansible/roles/evaluation-tool/README.md#evaluation-tool)
   * [Directory structure](ansible/roles/evaluation-tool/README.md#directory-structure)
   * [Get information from managed nodes (1)](ansible/roles/evaluation-tool/README.md#get-information-from-managed-nodes-1)
      + [Flowchart](ansible/roles/evaluation-tool/README.md#flowchart)
      + [Files and Structure](ansible/roles/evaluation-tool/README.md#files-and-structure)
      + [How It Works](ansible/roles/evaluation-tool/README.md#how-it-works)
      + [How to make changes](ansible/roles/evaluation-tool/README.md#how-to-make-changes)
      + [Debugging](ansible/roles/evaluation-tool/README.md#debugging)
   * [AI Module (2)](ansible/roles/evaluation-tool/README.md#ai-module-2)
      + [Flowchart](ansible/roles/evaluation-tool/README.md#flowchart-1)
      + [Files and Structure](ansible/roles/evaluation-tool/README.md#files-and-structure-1)
      + [How It Works](ansible/roles/evaluation-tool/README.md#how-it-works-1)
      + [How to make changes](ansible/roles/evaluation-tool/README.md#how-to-make-changes-1)
      + [Debugging](ansible/roles/evaluation-tool/README.md#debugging-1)
   * [Changing output directory structure, node names or report file names (3)](ansible/roles/evaluation-tool/README.md#changing-output-directory-structure-node-names-or-report-file-names-3)