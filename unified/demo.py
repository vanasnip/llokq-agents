#!/usr/bin/env python3
"""
Demo script to showcase unified system functionality
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from unified.agents.manager import AgentManager
from unified.core.command_parser import CommandParser
from unified.core.phase_manager import PhaseManager
from unified.core.command_executor import CommandExecutor
from unified.workflows.engine import WorkflowEngine
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def demo_agents():
    """Demo agent functionality"""
    console.print(Panel("[bold cyan]Agent Management Demo[/bold cyan]", expand=False))
    
    # Initialize agent manager
    agent_manager = AgentManager()
    
    # Show available agents
    console.print("\n[yellow]Available Agents:[/yellow]")
    for agent in agent_manager.agents.values():
        console.print(f"  • {agent.command} - {agent.identity.split('|')[0].strip()}")
    
    # Activate backend agent
    console.print("\n[yellow]Activating backend agent...[/yellow]")
    backend = agent_manager.activate_agent('backend')
    console.print(f"[green]Activated:[/green] {backend.identity}")
    console.print(f"[cyan]Core Belief:[/cyan] {backend.core_belief}")
    console.print(f"[cyan]MCP Preferences:[/cyan] {', '.join(backend.mcp_preferences)}")


def demo_command_execution():
    """Demo command execution"""
    console.print("\n")
    console.print(Panel("[bold cyan]Command Execution Demo[/bold cyan]", expand=False))
    
    # Initialize components
    agent_manager = AgentManager()
    command_parser = CommandParser(agent_manager)
    command_executor = CommandExecutor()
    
    # Parse a command
    command_str = "/code --backend --frontend"
    console.print(f"\n[yellow]Parsing command:[/yellow] {command_str}")
    
    parsed = command_parser.parse(command_str)
    console.print(f"[green]Base command:[/green] {parsed.base_command}")
    console.print(f"[green]Agents:[/green] {', '.join(parsed.agents)}")
    
    # Execute command
    agents = [agent_manager.get_agent(name) for name in parsed.agents]
    agents = [a for a in agents if a]
    
    console.print("\n[yellow]Executing command...[/yellow]")
    result = command_executor.execute(parsed, agents)
    
    if result['status'] == 'success':
        console.print(f"[green]✓ {result['message']}[/green]")
        console.print(f"[cyan]MCP Priority:[/cyan] {', '.join(result['mcp_config']['priority_order'])}")


def demo_workflow():
    """Demo workflow functionality"""
    console.print("\n")
    console.print(Panel("[bold cyan]Workflow Demo[/bold cyan]", expand=False))
    
    # Initialize components
    agent_manager = AgentManager()
    phase_manager = PhaseManager(agent_manager)
    workflow_engine = WorkflowEngine(agent_manager, phase_manager)
    
    # Start feature workflow
    console.print("\n[yellow]Starting feature development workflow...[/yellow]")
    result = workflow_engine.start_workflow('feature')
    
    if result['status'] != 'success':
        console.print(f"[red]Error: {result['message']}[/red]")
        return
    
    if result['status'] == 'success':
        console.print(f"[green]✓ {result['message']}[/green]")
        
        # Show workflow info
        workflow_info = result['workflow']
        console.print(f"[cyan]Workflow:[/cyan] {workflow_info['workflow']}")
        console.print(f"[cyan]Total steps:[/cyan] {workflow_info['total_steps']}")
        
        # Show next step
        next_step = result['next_step']
        console.print(f"\n[yellow]First step:[/yellow] {next_step['name']}")
        console.print(f"[cyan]Description:[/cyan] {next_step['description']}")
        console.print(f"[cyan]Agents:[/cyan] {', '.join(next_step['agents'])}")
        
        # Execute first step
        console.print("\n[yellow]Executing first step...[/yellow]")
        step_result = workflow_engine.execute_next_step()
        
        if step_result['status'] == 'success':
            console.print(f"[green]✓ {step_result['message']}[/green]")
            
            # Show workflow status
            status = workflow_engine.get_workflow_status()
            console.print(f"\n[cyan]Progress:[/cyan] {status['progress']:.0f}% complete")


def demo_phases():
    """Demo phase management"""
    console.print("\n")
    console.print(Panel("[bold cyan]Phase Management Demo[/bold cyan]", expand=False))
    
    # Initialize components
    agent_manager = AgentManager()
    phase_manager = PhaseManager(agent_manager)
    
    # Show current phase
    current = phase_manager.get_current_phase()
    console.print(f"\n[yellow]Current Phase:[/yellow] Phase {current.number} - {current.name}")
    console.print(f"[cyan]Lead Agent:[/cyan] {current.lead_agent}")
    console.print(f"[cyan]Required Outputs:[/cyan] {', '.join(current.outputs)}")
    
    # Show validation criteria
    console.print(f"[cyan]Validation Criteria:[/cyan]")
    for criteria in current.validation_criteria:
        console.print(f"  • {criteria}")


def main():
    """Run all demos"""
    console.print(Panel.fit(
        "[bold green]Unified D3P-SuperClaude System Demo[/bold green]\n"
        "Showcasing agent management, command execution, workflows, and phases",
        border_style="green"
    ))
    
    # Run demos
    demo_agents()
    demo_command_execution()
    demo_workflow()
    demo_phases()
    
    console.print("\n[bold green]✓ Demo complete![/bold green]")


if __name__ == '__main__':
    main()