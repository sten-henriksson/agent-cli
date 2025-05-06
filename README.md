# Agent CLI

A powerful interactive command-line interface for batch execution of agent tasks using various LLM models. The Agent CLI allows you to send prompts to AI agents, manage execution settings, and monitor request statuses.

## Features

- Interactive CLI with command history and auto-suggestions
- Support for multiple LLM models and agent methods
- Configuration via YAML files

## Installation

### Using pipx (recommended)

[pipx](https://pypa.github.io/pipx/) is recommended for installing CLI applications as it creates isolated environments:

```bash
# Install pipx if you don't have it
python -m pip install --user pipx
python -m pipx ensurepath

# Install agent-cli
pipx install git+https://github.com/sten-henriksson/agent-cli.git
```

### Using pip

```bash
pip install git+https://github.com/sten-henriksson/agent-cli.git
```

## Configuration

Create a YAML configuration file (`agent_config.yaml` by default) with your settings:
# getting gh token
1. Go to 
![image](https://github.com/user-attachments/assets/94558f67-c1e4-495b-9cbe-416607bb8361)
![image](https://github.com/user-attachments/assets/2ab44e29-504c-45f6-8536-7bf472859b11)

```yaml
defaults:
  gh_token: "your_github_token"  # Optional GitHub token
  repo: "your_repo"              # Default repository
  org: "your_organization"       # Default organization
  source_branch: "main"          # The branch to clone and base work on 
  target_branch: "main"          # The branch to create the PR against
  branch_prefix: "branch_prefix_example"

agents:
  - method: "open_hands"         # Agents currently, open_hands, aider, swe_agent_anth, swe_agent_default
    batch: 3                     # Number of concurrent requests
    model: "openrouter/google/gemini-2.5-flash-preview"
    llm_base_url: "https://openrouter.ai/api/v1"
    llm_api_key: "your_api_key"

remotes:
  - name: "main"
    ip: "127.0.0.1"             # Remote agent server IP
    port: 8089                  # Remote agent server port
```

## Usage

### Interactive Mode

Start the interactive CLI:

```bash
acomp --config your_config.yaml
```

### Direct Execution

Execute a prompt directly:

```bash
acomp --config your_config.yaml --prompt "Create a Python function to calculate Fibonacci numbers"
```

### Available Commands

In the interactive CLI, you can use the following commands:

- `/help` - Show available commands
- `/config` - Show current configuration
- `/remotes` - List configured remote agents
- `/jobs` - List running and completed jobs
- `/exit` - Quit the CLI
- `/clear` - Clear the terminal screen







