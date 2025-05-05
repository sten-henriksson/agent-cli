# Agent CLI

A powerful interactive command-line interface for batch execution of agent tasks using various LLM models. The Agent CLI allows you to send prompts to AI agents, manage execution settings, and monitor request statuses.

## Features

- Interactive CLI with command history and auto-suggestions
- Support for multiple LLM models and agent methods
- Remote execution with status polling
- Configuration via YAML files
- Support for GitHub integration
- Batch execution capabilities

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

```yaml
defaults:
  gh_token: "your_github_token"  # Optional GitHub token
  repo: "your_repo"              # Default repository
  org: "your_organization"       # Default organization
  model: "gpt-4"                 # Default model
  batch: 1                       # Default batch size
  method: "swe_agent_default"    # Default agent method

agents:
  - method: "open_hands"
    batch: 3
    model: "openrouter/google/gemini-2.5-flash-preview"
    llm_base_url: "https://openrouter.ai/api/v1"
    llm_api_key: "your_api_key"

remotes:
  - name: "main"
    ip: "127.0.0.1"  # Remote agent server IP
    port: 8089       # Remote agent server port
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
- `text without / prefix` - Automatically treated as a prompt to run

You can also configure parameters:
- `/method [value]` - Get/set the agent method
- `/model [value]` - Get/set the model
- `/batch [value]` - Get/set the batch size
- `/org [value]` - Get/set the organization
- `/repo [value]` - Get/set the repository

## Remote Execution

The CLI can connect to remote agent servers to execute prompts and poll for results. Configure the remote servers in your configuration file.

## Development

### Setting up for development

```bash
# Clone the repository
git clone https://github.com/sten-henriksson/agent-cli.git
cd agent-cli

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT

## Troubleshooting

### Command Not Found

If you get `command not found` after installation, try:

1. Make sure your PATH includes the pip or pipx installation directory
2. Try running with the Python module syntax: `python -m agent_cli.cli`
3. Reinstall using `pip install -e .` from the project directory

### Connection Issues

If you encounter connection issues with remote agents:

1. Verify the IP and port in your configuration
2. Check that the remote agent server is running
3. Ensure network connectivity between your machine and the server
