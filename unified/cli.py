#!/usr/bin/env python3
"""
Unified D3P-SuperClaude CLI
Main entry point for the unified agent system
"""
import click
import sys
import os
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Handle imports whether installed or running from source
try:
    from unified import __version__
    from unified.agents.manager import AgentManager
    from unified.core.command_parser import CommandParser
    from unified.core.phase_manager import PhaseManager
    from unified.core.command_executor import CommandExecutor
    from unified.workflows.engine import WorkflowEngine
except ImportError:
    # Add parent directory to path for development
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from unified import __version__
    from unified.agents.manager import AgentManager
    from unified.core.command_parser import CommandParser
    from unified.core.phase_manager import PhaseManager
    from unified.core.command_executor import CommandExecutor
    from unified.workflows.engine import WorkflowEngine

console = Console()


class UnifiedCLI:
    """Main CLI handler for the unified system"""
    
    def __init__(self):
        # Initialize with automatic agent conversion if needed
        self._ensure_agent_config()
        
        self.agent_manager = AgentManager()
        self.command_parser = CommandParser(self.agent_manager)
        self.phase_manager = PhaseManager(self.agent_manager)
        self.command_executor = CommandExecutor()
        self.workflow_engine = WorkflowEngine(self.agent_manager, self.phase_manager)
    
    def _ensure_agent_config(self):
        """Ensure agent configuration exists, convert if needed"""
        config_path = Path.home() / ".claude" / "agents.yml"
        
        if not config_path.exists():
            console.print("[yellow]First time setup: Converting agent definitions...[/yellow]")
            
            # Find package installation or local directory
            if __package__:
                # Installed package
                package_dir = Path(__file__).parent.parent
            else:
                # Running from source
                package_dir = Path(__file__).parent.parent
            
            # Run conversion
            from unified.scripts.convert_agents import main as convert_agents
            
            # Create config directory
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Change to package directory for conversion
            original_cwd = os.getcwd()
            os.chdir(package_dir)
            
            try:
                convert_agents()
                console.print("[green]✓ Agent configuration created successfully![/green]")
            finally:
                os.chdir(original_cwd)
    
    def show_agents(self):
        """Display available agents in a table"""
        table = Table(title="Available Agents", show_header=True, header_style="bold magenta")
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Category", style="yellow")
        table.add_column("Identity", style="white")
        
        for agent in sorted(self.agent_manager.agents.values(), key=lambda a: a.category.value):
            identity_short = agent.identity.split('|')[0].strip()
            table.add_row(
                agent.command,
                agent.name,
                agent.category.value,
                identity_short
            )
        
        console.print(table)
    
    def show_phase_status(self):
        """Display current phase status"""
        status = self.phase_manager.get_phase_status()
        
        panel_content = f"""
[bold]Phase {status['phase']}: {status['name']}[/bold]
{status['description']}

[yellow]Lead Agent:[/yellow] {status['lead_agent']}
[yellow]Active Agents:[/yellow] {', '.join(status['active_agents']) if status['active_agents'] else 'None'}

[yellow]Progress:[/yellow] {status['completion']:.0f}%
"""
        
        # Add output status
        if status['outputs']:
            panel_content += "\n[yellow]Outputs:[/yellow]\n"
            for output, completed in status['outputs'].items():
                icon = "✓" if completed else "○"
                panel_content += f"  {icon} {output}\n"
        
        console.print(Panel(panel_content, title="D3P Phase Status", border_style="blue"))
    
    def execute_command(self, command_str: str):
        """Parse and execute a command"""
        try:
            # Parse command
            parsed = self.command_parser.parse(command_str)
            
            # Validate agents
            valid, invalid = self.command_parser.validate_agents(parsed.agents)
            if not valid:
                console.print(f"[red]Error: Unknown agents: {', '.join(invalid)}[/red]")
                return
            
            # Apply agent context
            context = self.command_parser.apply_agent_context(parsed)
            
            # Handle different command types
            if parsed.base_command == 'agent':
                if '--list' in command_str:
                    self.show_agents()
                elif '--info' in command_str:
                    agent_name = command_str.split('--info')[-1].strip()
                    self.show_agent_info(agent_name)
            
            elif parsed.base_command == 'phase':
                if '--current' in command_str or '--status' in command_str:
                    self.show_phase_status()
                elif '--next' in command_str:
                    if self.phase_manager.advance_phase():
                        console.print("[green]Advanced to next phase[/green]")
                        self.show_phase_status()
                    else:
                        console.print("[yellow]Cannot advance - current phase not complete[/yellow]")
                elif parsed.options.get('goto'):
                    phase_num = int(parsed.options['goto'])
                    if self.phase_manager.goto_phase(phase_num):
                        console.print(f"[green]Jumped to phase {phase_num}[/green]")
                        self.show_phase_status()
                    else:
                        console.print(f"[red]Invalid phase number: {phase_num}[/red]")
            
            elif parsed.base_command == 'workflow':
                workflow_type = parsed.options.get('workflow_type')
                if workflow_type:
                    result = self.workflow_engine.start_workflow(workflow_type)
                    if result['status'] == 'success':
                        console.print(f"[green]{result['message']}[/green]")
                        console.print(f"[cyan]Next step: {result['next_step']['name']}[/cyan]")
                        console.print(f"[yellow]Description: {result['next_step']['description']}[/yellow]")
                        console.print(f"[yellow]Agents: {', '.join(result['next_step']['agents'])}[/yellow]")
                    else:
                        console.print(f"[red]{result['message']}[/red]")
                elif '--status' in command_str:
                    status = self.workflow_engine.get_workflow_status()
                    self.show_workflow_status(status)
                elif '--next' in command_str:
                    result = self.workflow_engine.execute_next_step()
                    if result['status'] == 'success':
                        console.print(f"[green]{result['message']}[/green]")
                        if result.get('next_step'):
                            console.print(f"[cyan]Next: {result['next_step']['name']}[/cyan]")
                    else:
                        console.print(f"[red]{result['message']}[/red]")
                else:
                    self.show_workflows()
            
            elif parsed.base_command == 'team':
                if parsed.options.get('activate'):
                    agents = parsed.options['activate']
                    if self.agent_manager.validate_agent_compatibility(agents):
                        for agent in agents:
                            self.agent_manager.activate_agent(agent)
                        console.print(f"[green]Activated agents: {', '.join(agents)}[/green]")
                    else:
                        console.print("[red]Agents are not compatible for parallel execution[/red]")
            
            else:
                # Regular command with agent context
                agents = [self.agent_manager.get_agent(name) for name in parsed.agents]
                agents = [a for a in agents if a]  # Filter None values
                
                result = self.command_executor.execute(parsed, agents)
                
                console.print(f"\n[bold]Executing:[/bold] {parsed.base_command}")
                if agents:
                    console.print(f"[bold]Active Agents:[/bold] {', '.join(a.name for a in agents)}")
                
                if result['status'] == 'success':
                    console.print(f"[green]{result['message']}[/green]")
                    if 'mcp_config' in result:
                        console.print(f"[cyan]MCP Priority:[/cyan] {', '.join(result['mcp_config']['priority_order'])}")
                else:
                    console.print(f"[red]{result['message']}[/red]")
        
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
    
    def show_agent_info(self, agent_name: str):
        """Display detailed information about an agent"""
        agent = self.agent_manager.get_agent(agent_name)
        if not agent:
            console.print(f"[red]Agent '{agent_name}' not found[/red]")
            return
        
        info = f"""
[bold cyan]{agent.name.upper()}[/bold cyan]
{agent.identity}

[yellow]Core Belief:[/yellow] {agent.core_belief}
[yellow]Primary Question:[/yellow] {agent.primary_question}
[yellow]Decision Framework:[/yellow] {agent.decision_framework}
[yellow]Risk Profile:[/yellow] {agent.risk_profile}

[yellow]Success Metrics:[/yellow] {agent.success_metrics}
[yellow]Communication Style:[/yellow] {agent.communication_style}
[yellow]Problem Solving:[/yellow] {agent.problem_solving}

[yellow]MCP Preferences:[/yellow] {', '.join(agent.mcp_preferences)}
[yellow]Focus Areas:[/yellow] {', '.join(agent.focus_areas)}
"""
        
        if agent.values:
            info += f"\n[yellow]Values:[/yellow] {agent.values}"
        if agent.limitations:
            info += f"\n[yellow]Limitations:[/yellow] {agent.limitations}"
        
        console.print(Panel(info, title=f"Agent: {agent.command}", border_style="cyan"))
    
    def show_workflows(self):
        """Display available workflows"""
        workflows = [
            ("feature", "Feature Development", "Complete feature from requirements to deployment"),
            ("bug", "Bug Investigation", "Systematic bug resolution process"),
            ("performance", "Performance Optimization", "Analyze and optimize system performance"),
            ("security", "Security Audit", "Comprehensive security assessment"),
            ("api", "API Development", "Design and implement new API endpoints"),
        ]
        
        table = Table(title="Available Workflows", show_header=True, header_style="bold magenta")
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Description", style="white")
        
        for cmd, name, desc in workflows:
            table.add_row(f"/workflow {cmd}", name, desc)
        
        console.print(table)
    
    def show_workflow_status(self, status: Dict[str, Any]):
        """Display workflow status"""
        if status['status'] == 'info':
            console.print("[yellow]No active workflow[/yellow]")
            console.print(f"Available workflows: {', '.join(status['available_workflows'])}")
            return
        
        panel_content = f"""
[bold]Workflow: {status['workflow']}[/bold]
Type: {status['type']}
State: {status['state']}

[yellow]Progress:[/yellow] {status['progress']:.0f}% ({status['current_step']}/{status['total_steps']} steps)
"""
        
        if status.get('current_step_info'):
            step = status['current_step_info']
            panel_content += f"""
[yellow]Current Step:[/yellow] {step['name']}
[yellow]Description:[/yellow] {step['description']}
[yellow]Agents:[/yellow] {', '.join(step['agents'])}
[yellow]Command:[/yellow] {step['command']}
"""
        
        console.print(Panel(panel_content, title="Workflow Status", border_style="blue"))


@click.group()
@click.version_option(version=__version__, prog_name='unified-agents')
def cli():
    """Unified D3P-SuperClaude Agent System
    
    A comprehensive AI agent development system with 15+ specialized agents
    for software development, from requirements gathering through deployment.
    
    Quick start:
        unified-agents interactive
    
    Or use the short alias:
        ua interactive
    """
    pass


@cli.command()
def agents():
    """List all available agents"""
    unified_cli = UnifiedCLI()
    unified_cli.show_agents()


@cli.command()
def status():
    """Show current phase status"""
    unified_cli = UnifiedCLI()
    unified_cli.show_phase_status()


@cli.command()
@click.argument('agent_name')
def info(agent_name):
    """Show detailed information about an agent"""
    unified_cli = UnifiedCLI()
    unified_cli.show_agent_info(agent_name)


@cli.command()
def interactive():
    """Start interactive mode"""
    unified_cli = UnifiedCLI()
    
    console.print("\n[bold cyan]Unified D3P-SuperClaude System[/bold cyan]")
    console.print("Type '/help' for available commands or 'exit' to quit\n")
    
    while True:
        try:
            command = input("[bold]>[/bold] ")
            
            if command.lower() in ['exit', 'quit']:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            elif command == '/help':
                help_text = unified_cli.command_parser.format_help()
                console.print(help_text)
            
            elif command.startswith('/'):
                unified_cli.execute_command(command)
            
            else:
                console.print("[yellow]Commands must start with /[/yellow]")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")


@cli.command()
def demo():
    """Run a demonstration of the system"""
    from unified.demo import main as run_demo
    run_demo()


@cli.command()
def setup():
    """Run initial setup and configuration"""
    unified_cli = UnifiedCLI()
    console.print("[green]✓ Setup complete! Agent configuration initialized.[/green]")
    console.print("\nTry these commands:")
    console.print("  unified-agents agents     # List all agents")
    console.print("  unified-agents interactive # Start interactive mode")
    console.print("  unified-agents demo       # Run demonstration")


if __name__ == '__main__':
    cli()