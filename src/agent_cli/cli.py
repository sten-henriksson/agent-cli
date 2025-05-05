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
    parser.add_argument('--source-branch',
                        type=str,
                        help='Source branch for the operation')
    parser.add_argument('--target-branch',
                        type=str,
                        help='Target branch for the operation')
    parser.add_argument('--branch-prefix',
                        type=str,
                        help='Branch prefix for the operation')
    args = parser.parse_args()
    
    if args.prompt:
        # Load configuration
        config = load_config(args.config)
        defaults = config.get('defaults', {})
        # Current values
        current_settings = {
            "org": defaults.get('org', "interactive"),
            "repo": defaults.get('repo', "cli"),
            "method": defaults.get('method', "swe_agent"),
            "batch": defaults.get('batch', 1),
            "model": defaults.get('model', "gpt-4"),
            "source_branch": args.source_branch or defaults.get('source_branch', "main"),
            "target_branch": args.target_branch or defaults.get('target_branch', "main"),
            "branch_prefix": args.branch_prefix or defaults.get('branch_prefix', "agent_router"),
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