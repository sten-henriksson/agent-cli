#!/usr/bin/env python3

import argparse
from agent_cli.main import interactive_cli, load_config, execute_run_command
from prompt_toolkit import PromptSession

def main():
    parser = argparse.ArgumentParser(description='Interactive Agent CLI for batch execution')
    parser.add_argument('--config',
                        type=str,
                        default="agent_config.yaml",
                        help='Path to the agent configuration YAML file (default: agent_config.yaml)')
    parser.add_argument('--prompt',
                        type=str,
                        help='Directly execute with this prompt instead of entering interactive mode')
    args = parser.parse_args()

    if args.prompt:
        # Load configuration
        config = load_config(args.config)
        defaults = config.get('defaults', {})
        # Current values
        current_settings = {
            "model": defaults.get('model', "gpt-4"),
            "batch": defaults.get('batch', 1),
            "method": defaults.get('method', "swe_agent_default"),
            "org": defaults.get('org', "interactive"),
            "repo": defaults.get('repo', "cli"),
        }
        remotes = config.get('remotes', [])
        # Execute directly with the provided prompt
        execute_run_command(
            prompt=args.prompt,
            current_settings=current_settings,
            config=config,
            remotes=remotes,
            session=PromptSession()
        )
    else:
        interactive_cli(args.config)

if __name__ == "__main__":
    main()