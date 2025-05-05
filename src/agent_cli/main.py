import asyncio
import json
import time
from typing import Dict, Any, List, Optional
  
import requests
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.markdown import Markdown
  
load_dotenv()
  
console = Console()
  
class AgentDetail(BaseModel):
    """Agent configuration details.

    Args:
        method (str): Name of the agent method to use (swe_agent/code_agent)
        batch (int): Number of parallel executions for this agent type
        model (str): LLM model identifier to use for this agent
        llm_base_url (str, optional): Base URL for LLM API
        llm_api_key (str, optional): API key for LLM service
    """
    method: str
    batch: int
    model: str
    llm_base_url: str = None
    llm_api_key: str = None

class AgentRequest(BaseModel):
    """Main request structure for batch execution endpoint.

    Args:
        prompt (str): Instruction prompt for agents to execute
        org (str): Source organization name
        repo (str): Target repository name
        agents (list[AgentDetail]): List of agent configurations
    """
    prompt: str
    org: str = None
    repo: str = None
    agents: list[AgentDetail]
    gh_token: str = None
    source_branch: str = "main"
    target_branch: str = "main"
    branch_prefix: str = "agent_router"
  
  
def load_config(config_path: str = "agent_config.yaml") -> Dict[str, Any]:
    """Load YAML configuration file."""
    try:
        with open(config_path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        console.print(f"[yellow]Warning: Config file {config_path} not found, using defaults[/yellow]")
        return {}
    except yaml.YAMLError as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        return {}
  
  
def get_multiline_input(session: PromptSession) -> str:
    """Get multiline input from the user using prompt_toolkit."""
    console.print("[blue]Enter your multiline prompt (press ESC followed by ENTER to finish):[/blue]")
    text = session.prompt(
        "> ",
        multiline=True,
        prompt_continuation="... ",
    )
    return text
  
  
def display_help():
    """Display help information using rich tables."""
    table = Table(title="Available Commands", show_header=True)
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="green")
    commands = [
        ("/help", "Show this help message"),
        ("/config", "Show current configuration"),
        ("/remotes", "List configured remote agents"),
        ("/exit", "Quit the CLI"),
        ("/clear", "Clear the terminal screen"),
        ("/jobs", "List running and completed jobs"),
        ("text without / prefix", "Automatically treated as a /run command")
    ]
    for cmd, desc in commands:
        table.add_row(cmd, desc)
    console.print(table)
  
  
def display_config(config_data: Dict[str, Any]):
    """Display configuration using rich tables."""
    table = Table(title="Current Configuration", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    for key, value in config_data.items():
        table.add_row(key, str(value))
    console.print(table)
  
  
def display_remotes(remotes: List[Dict[str, Any]]):
    """Display remote agents using rich tables."""
    if not remotes:
        console.print("[yellow]No remote agents configured[/yellow]")
        return
    table = Table(title="Configured Remote Agents", show_header=True)
    table.add_column("#", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("IP", style="green")
    table.add_column("Port", style="green")
    for i, remote in enumerate(remotes, 1):
        table.add_row(str(i), remote['name'], remote['ip'], str(remote['port']))
    console.print(table)
  
  
async def poll_status(remote: Dict[str, Any], request_id: str):
    """Poll for status updates from remote agent."""
    status_url = f"http://{remote['ip']}:{remote['port']}/status/request/{request_id}"
    with console.status("[blue]Polling for status updates...[/blue]") as status:
        while True:
            try:
                status_response = requests.get(status_url)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status_text = status_data.get('status', 'Unknown')
                    console.print(f"[blue]Status:[/blue] {status_text}")
                    if status_text in ['completed', 'failed']:
                        console.print("[green]Final result:[/green]")
                        console.print(Syntax(json.dumps(status_data, indent=2), "json"))
                        break
                else:
                    console.print(f"[yellow]Status check failed: {status_response.text}[/yellow]")
            except Exception as e:
                console.print(f"[red]Error polling status: {str(e)}[/red]")
                break
            await asyncio.sleep(3)  # Update every 3 seconds
  
  
def execute_run_command(prompt: str, current_settings: Dict[str, Any],
                     config: Dict[str, Any], remotes: List[Dict[str, Any]],
                     session: PromptSession):
    """Execute the run command with the given prompt."""
    # If the prompt is short, ask if they want multiline
    if len(prompt) < 50 and not prompt.endswith("..."):
        if session.prompt("Do you want to enter a multiline prompt? (y/n): ").lower().startswith('y'):
            prompt = get_multiline_input(session)
    if not prompt:
        console.print("[yellow]Prompt cannot be empty[/yellow]")
        return
    # Display the prompt
    console.print(Panel(prompt, title="Prompt", border_style="green"))
    # Use configured agents if available, otherwise use current settings
    agents = config.get('agents', [])
    if not agents:
        agents = [{
            'method': current_settings['method'],
            'batch': current_settings['batch'],
            'model': current_settings['model']
        }]
    request = AgentRequest(
        prompt=prompt,
        org=current_settings['org'],
        repo=current_settings['repo'],
        agents=[AgentDetail(**a) for a in agents],
        gh_token=config.get("defaults", {}).get("gh_token"),
        source_branch=current_settings['source_branch'],
        target_branch=current_settings['target_branch'],
        branch_prefix=current_settings['branch_prefix']
    )
    # Check if we should execute remotely
    if remotes:
        remote_exec = remotes[0]
        console.print(f"[blue]Executing on remote:[/blue] {remote_exec['name']}")
        try:
            url = f"http://{remote_exec['ip']}:{remote_exec['port']}/execute_batch"
            with console.status("[blue]Sending request...[/blue]"):
                # Using model_dump() for Pydantic v2 compatibility
                response = requests.post(url, json=request.model_dump())
            if response.status_code == 200:
                console.print("[green]Remote execution successful:[/green]")
                console.print(Syntax(json.dumps(response.json(), indent=2), "json"))
                # Poll for status updates
                request_id = response.json().get("request_id")
                if request_id:
                    console.print(f"[blue]Tracking request ID:[/blue] {request_id}")
                    try:
                        asyncio.run(poll_status(remote_exec, request_id))
                    except KeyboardInterrupt:
                        console.print("\n[yellow]Stopped status polling. Request is still processing.[/yellow]")
            else:
                console.print(f"[red]Remote execution failed:[/red] {response.text}")
        except Exception as e:
            console.print(f"[red]Error connecting to remote:[/red] {str(e)}")
    else:
        # Handle local execution here
        console.print("[yellow]Local execution not implemented yet[/yellow]")
  
  
def interactive_cli(config_path: str = "agent_config.yaml"):
    """Interactive command line interface for batch execution using prompt_toolkit and rich."""
    # Load configuration
    config = load_config(config_path)
    defaults = config.get('defaults', {})
    # Current values
    current_settings = {
        "org": defaults.get('org', "interactive"),
        "repo": defaults.get('repo', "cli"),
        "source_branch": defaults.get('source_branch', "main"),
        "target_branch": defaults.get('target_branch', "main"),
        "branch_prefix": defaults.get('branch_prefix', "agent_router"),
    }
    remotes = config.get('remotes', [])
    # Set up prompt toolkit
    command_completer = WordCompleter([
        '/help', '/config', '/remotes',  '/exit', '/clear','/jobs'
    ])
    style = Style.from_dict({
        'prompt': '#00aa00 bold',
    })
    history = FileHistory('.agent_cli_history')
    session = PromptSession(
        history=history,
        auto_suggest=AutoSuggestFromHistory(),
        completer=command_completer,
        style=style,
    )
    # Welcome message
    console.print(Panel.fit(
        "[bold cyan]Interactive Agent CLI[/bold cyan]\n"
        "[green]Type your commands (type /help for options) or start typing to run a prompt[/green]",
        border_style="blue"
    ))
  
    while True:
        try:
            user_input = session.prompt("agent-cli> ").strip()
            if not user_input:
                continue
            # Handle commands
            if user_input.startswith('/'):
                cmd_parts = user_input[1:].split(maxsplit=1)
                cmd = cmd_parts[0].lower()
                args = cmd_parts[1] if len(cmd_parts) > 1 else ""
                if cmd == "help":
                    display_help()
                elif cmd == "run":
                    if args:
                        # Use everything after "/run " as the prompt
                        prompt = args
                    else:
                        # Ask for multiline input
                        prompt = get_multiline_input(session)
                    execute_run_command(
                        prompt=prompt,
                        current_settings=current_settings,
                        config=config,
                        remotes=remotes,
                        session=session
                    )
                elif cmd == "exit":
                    console.print("[green]Goodbye![/green]")
                    break
                elif cmd == "config":
                    display_config(current_settings)
  
                elif cmd == "remotes":
                    display_remotes(remotes)
  
                elif cmd == "jobs":
                    try:
                        url = f"http://{remotes[0]['ip']}:{remotes[0]['port']}/status/requests"
                        response = requests.get(url)
                        response.raise_for_status()
                        jobs = response.json()
  
                        table = Table(title="Agent Requests")
                        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
                        table.add_column("Timestamp", style="magenta")
                        table.add_column("Method", style="green")
                        table.add_column("Status", style="red")
                        table.add_column("Prompt", style="yellow")
                        table.add_column("Org", style="blue")
                        table.add_column("Repo", style="blue")
  
                        for job in reversed(jobs):
                            table.add_row(
                                str(job["id"]),
                                job["timestamp"],
                                job["method"],
                                job["status"],
                                job["prompt"],
                                job["org"],
                                job["repo"]
                            )
  
                        console.print(table)
                    except Exception as e:
                        console.print(f"[red]Error fetching jobs:[/red] {str(e)}")
  
                elif cmd == "clear":
                    console.clear()
                else:
                    console.print(f"[red]Unknown command: /{cmd}[/red]")
                    console.print("Type [green]/help[/green] for options")
            else:
                # Default to /run if text is entered without a command prefix
                console.print("[dim]Executing as prompt...[/dim]")
                execute_run_command(
                    prompt=user_input,
                    current_settings=current_settings,
                    config=config,
                    remotes=remotes,
                    session=session
                )
        except KeyboardInterrupt:
            console.print("\n[yellow]Press Ctrl+D or type /exit to quit[/yellow]")
        except EOFError:
            console.print("\n[green]Goodbye![/green]")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
  
  
