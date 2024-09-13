# Ansible
##  Setup
### Add correct user to ansible.cfg
Update `remote_user` in `ansible.cfg` for your user

### Add clouds.yml file
Example clouds.yml file in root of ansible directory
```yml
clouds:
  engines:    
    auth:
      auth_url: https://auth_url.ch/v3      
      application_credential_id: "application_credential_id"
      application_credential_secret: "application_credential_secret-UQozBNdsZds8SKt44EtS0_WJ4wraD3uKsYTrtoGuK_w"
    region_name: "region_name"    
    interface: "public"
    identity_api_version: 3
    auth_type: "v3applicationcredential"
```

### Setup python virtual environment and required python packages
Navigate to `./ansible` directory.

Create virtual environment
```bash
python3 -m venv venv-name
```

Activate virtual environment
```bash
source venv-name/bin/activate
```

Install requirements
```bash
pip install -r requirements.txt
```

### LLM config
Update the [config](./roles/evaluation-tool/vars/llm_config.yml) with you API key credentials (or just use ours)

```yml
gpt:
  model: gpt-4o
  api_key: {YOUR_OPEN_AI_API_KEY}
groq:
  api_key: {YOUR_GROQ_API_KEY}
  models:
     ...
ollama:
  model: llama3.1
```

[How to get {YOUR_OPEN_AI_API_KEY}](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key)

[How to get {YOUR_GROQ_API_KEY}](https://www.kerlig.com/help/groq/get-api-key)

### How to install Ollama
Prerequisite:
* [Install Ollama for your OS](https://ollama.com/download)
* Docker installed

Open Terminal that can handle bash (for Windows use Git Bash) and go to path 
```bash
cd /your/path/to/ai-based-operating-system/ansible/sandbox-files
```

Make the script executable
```bash
chmod +x init_ollama.sh
```

Run the script
```bash
./init_ollama.sh
```

[If you want to use GPU acceleration, please follow this documentation.](https://ollama.com/blog/ollama-is-now-available-as-an-official-docker-image)

## How to run
### In the ansible/ directory of this repository
#### Run playbook with default LLM (=gpt)
```bash
ansible-playbook main.yml
```
#### Run playbook with selected LLM (take a look at [the LLM configuration file](./roles/evaluation-tool/vars/llm_config.yml))
```bash
ansible-playbook main.yml --extra-vars 'llm_name="{identifier}"'
```
Available identifiers:
```yml
identifiers:
  online:
    - gpt
    - groq
    - groq-mixtral
    - groq-gemma
    - groq-gemma2

  offline:
    - ollama
```
#### Turn of information processing from the managed nodes to only run AI Requests
```bash
ansible-playbook main.yml --extra-vars 'no_processing=true'
```
#### Turn of AI Requests and only process the information on the managed nodes

```bash
ansible-playbook main.yml --extra-vars 'no_ai=true'
```

## How to use in other repos
### Add to another file in this repo
```yml
- name: Gather system information
  hosts: all                    # override with hostX or host1, host2
  become: yes                   # yes
  gather_facts: false           # true if debug
  roles:                        # add role evaluation tool
    - evaluation-tool
  vars:                         # override remote_user and ansible_user value with your user
    remote_user: debian
    ansible_user: debian
```

### As a role for another file/ project
For another project copy the role first to the respective roles directory
```bash
cp -r \
  ./ai-based-operating-system-evaluation/ansible/roles/evalation-tool \
  ./path/to/your/ansible/roles/evaluation-tool
```

Use the role in another file
```yml
- name: Gather system information
  hosts: all                    # override with hostX or host1, host2
  become: yes                   # yes
  gather_facts: false           # true if debug
  roles:                        # add role evaluation tool
    - evaluation-tool
  vars:                         # override remote_user and ansible_user value with your user
    remote_user: debian
    ansible_user: debian
```