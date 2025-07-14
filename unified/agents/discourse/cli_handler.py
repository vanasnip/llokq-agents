"""
CLI handler for discourse mode integration
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from unified.agents.discourse import (
    DiscourseAgent,
    DiscourseCommandParser,
    ConversationPhase,
    EntryType
)


class DiscourseCLIHandler:
    """Handles discourse mode interactions in the CLI"""
    
    def __init__(self, discourse_agent: DiscourseAgent):
        self.discourse = discourse_agent
        self.parser = DiscourseCommandParser()
        self.console = Console()
        self.in_discourse_mode = False
    
    def enter_discourse_mode(self):
        """Enter discourse mode with welcome message"""
        self.in_discourse_mode = True
        
        welcome = Panel(
            """[bold cyan]Discourse Mode Activated[/bold cyan]
            
I'm now your conversational facilitator. I'll help you:
• Explore ideas through structured discussion
• Capture insights and decisions
• Organize knowledge systematically
• Export conversations for future reference

All operations are [bold yellow]READ-ONLY[/bold yellow] - no files will be modified.

Type [cyan]/help[/cyan] for available commands or start discussing!""",
            title="💭 Discourse Mode",
            border_style="cyan"
        )
        
        self.console.print(welcome)
        
        # Show current phase
        self._show_phase_indicator()
    
    def exit_discourse_mode(self):
        """Exit discourse mode"""
        self.in_discourse_mode = False
        
        # Show exit message
        self.console.print("\n[yellow]Exiting Discourse Mode[/yellow]")
        
        # Show final stats
        stats = self.get_conversation_stats()
        if stats['total_entries'] > 0:
            self.console.print(f"\nConversation Summary:")
            self.console.print(f"  • Total Entries: {stats['total_entries']}")
            self.console.print(f"  • Decisions Made: {stats['decisions']}")
            self.console.print(f"  • Topics Covered: {stats['topics']}")
            
            self.console.print("\n[dim]Use /export to save this conversation[/dim]")
        
        self.console.print("\n[cyan]Returning to normal mode[/cyan]")
    
    def handle_command(self, command_str: str) -> bool:
        """
        Handle a discourse command.
        Returns True if handled, False if not a discourse command.
        """
        if not command_str.startswith('/'):
            # Natural language input - convert to question
            if self.in_discourse_mode and command_str.strip():
                result = self.discourse.execute('question', {
                    'question': command_str.strip()
                })
                self._display_result(result)
                return True
            return False
        
        # Check for help
        if command_str.strip() == '/help':
            self._show_help()
            return True
        
        # Check for exit discourse mode
        if command_str.strip() == '/exit-discourse':
            self.exit_discourse_mode()
            return True
        
        # Parse discourse command
        cmd = self.parser.parse(command_str)
        if not cmd:
            return False
        
        # Validate command
        valid, error = self.parser.validate_command(cmd)
        if not valid:
            self.console.print(f"[red]Error: {error}[/red]")
            return True
        
        # Execute command
        result = self.discourse.execute(cmd.command, cmd.options)
        self._display_result(result)
        
        # Show phase indicator after phase transitions
        if cmd.command == 'phase' and result['status'] == 'success':
            self._show_phase_indicator()
        
        return True
    
    def _display_result(self, result: Dict[str, Any]):
        """Display command result in a user-friendly way"""
        if result['status'] == 'error':
            self.console.print(f"[red]❌ {result['message']}[/red]")
            return
        
        # Handle different result types
        if 'entry_id' in result:
            self.console.print(f"[green]✓[/green] Entry {result['entry_id']} added")
        
        elif 'summary' in result:
            self._display_summary(result['summary'])
        
        elif 'outline' in result:
            self._display_outline(result['outline'])
        
        elif 'context' in result:
            self._display_context(result['context'])
        
        elif 'results' in result:
            self._display_search_results(result['results'])
        
        elif 'markdown_preview' in result:
            # Archive preview
            self.console.print("\n[bold]Archive Preview:[/bold]")
            self.console.print(Panel(
                result['markdown_preview'],
                title="📄 Archive Content",
                border_style="green"
            ))
            self.console.print(f"\n[yellow]Note: {result['note']}[/yellow]")
        
        else:
            # Generic success message
            self.console.print(f"[green]✓[/green] {result['message']}")
    
    def _display_summary(self, summary: Dict[str, Any]):
        """Display conversation summary"""
        panel_content = f"""[bold]Conversation Summary[/bold]

Total Entries: {summary['total_entries']}
Current Phase: [cyan]{summary['phase']}[/cyan]
Categories: {', '.join(summary['categories']) if summary['categories'] else 'None'}
Decisions Made: {summary['decisions_made']}"""
        
        self.console.print(Panel(panel_content, border_style="blue"))
        
        # Show recent entries if available
        if 'recent_entries' in summary:
            self.console.print("\n[bold]Recent Activity:[/bold]")
            for entry in summary['recent_entries'][-3:]:
                self.console.print(
                    f"  • [{entry['type']}] {entry['content'][:80]}..."
                    if len(entry['content']) > 80 else f"  • [{entry['type']}] {entry['content']}"
                )
    
    def _display_outline(self, outline: Dict[str, Any]):
        """Display conversation outline"""
        self.console.print(f"\n[bold]{outline['title']}[/bold]\n")
        
        # Display phases
        for phase, data in outline['phases'].items():
            if data['entry_count'] > 0:
                self.console.print(f"[cyan]{phase.title()} Phase[/cyan] ({data['entry_count']} entries)")
                for entry in data['entries'][:3]:  # Show first 3
                    self.console.print(f"  • [{entry['type']}] {entry['summary']}")
                if data['entry_count'] > 3:
                    self.console.print(f"  • ... and {data['entry_count'] - 3} more")
                self.console.print()
        
        # Display decisions
        if outline['decisions']:
            self.console.print("[bold]Key Decisions:[/bold]")
            for decision in outline['decisions']:
                self.console.print(f"  ✓ {decision['decision']}")
    
    def _display_context(self, context: Dict[str, Any]):
        """Display current context"""
        table = Table(title="Current Context", show_header=True, header_style="bold magenta")
        table.add_column("Attribute", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Phase", context['phase'].title())
        table.add_row("Total Entries", str(context['total_entries']))
        table.add_row("Topics", ', '.join(context['topics']) if context['topics'] else 'None')
        table.add_row("Categories", ', '.join(context['categories']) if context['categories'] else 'None')
        table.add_row("Decisions Made", str(context['decisions_made']))
        
        self.console.print(table)
    
    def _display_search_results(self, results: List[Dict[str, Any]]):
        """Display search results"""
        if not results:
            self.console.print("[yellow]No matching entries found[/yellow]")
            return
        
        self.console.print(f"\n[bold]Found {len(results)} entries:[/bold]\n")
        
        for entry in results:
            # Format entry display
            header = f"[{entry['type']}] {entry['id']} - {entry['phase']}"
            if entry.get('category'):
                header += f" ({entry['category']})"
            
            self.console.print(f"[cyan]{header}[/cyan]")
            self.console.print(f"{entry['content'][:200]}..." 
                             if len(entry['content']) > 200 
                             else entry['content'])
            
            if entry.get('references'):
                self.console.print(f"[dim]References: {', '.join(entry['references'])}[/dim]")
            
            self.console.print()
    
    def _show_phase_indicator(self):
        """Show current conversation phase"""
        phase = self.discourse.conversation.current_phase
        
        phase_descriptions = {
            ConversationPhase.EXPLORATION: "🔍 Asking questions and gathering context",
            ConversationPhase.ANALYSIS: "🔬 Breaking down the problem",
            ConversationPhase.SYNTHESIS: "🧩 Combining insights",
            ConversationPhase.DECISION: "✅ Making choices",
            ConversationPhase.ARCHIVE: "📚 Preserving knowledge"
        }
        
        self.console.print(
            f"\n[bold]Current Phase:[/bold] [cyan]{phase.value.title()}[/cyan] - "
            f"{phase_descriptions.get(phase, 'Progressing through discussion')}"
        )
    
    def _show_help(self):
        """Show discourse mode help"""
        help_text = self.parser.get_help()
        
        self.console.print("\n[bold cyan]Discourse Mode Commands[/bold cyan]\n")
        self.console.print(help_text)
        
        self.console.print("\n[bold]Tips:[/bold]")
        self.console.print("• Type naturally - your input becomes questions")
        self.console.print("• Use /phase to progress the conversation")
        self.console.print("• Use /export when ready to save the discussion")
        self.console.print("• All operations are read-only\n")
    
    def export_conversation(self, format_type: str = 'markdown') -> Optional[str]:
        """Export the current conversation"""
        result = self.discourse.execute('archive', {})
        
        if result['status'] == 'success':
            archive_data = self.discourse.conversation.prepare_archive()
            
            if format_type == 'markdown':
                return archive_data['markdown']
            elif format_type == 'json':
                import json
                return json.dumps(archive_data['data'], indent=2)
            else:
                return None
        
        return None
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        context = self.discourse.conversation.get_current_context()
        
        return {
            'phase': context['phase'],
            'total_entries': context['total_entries'],
            'topics': len(context['topics']),
            'categories': len(context['categories']),
            'decisions': context['decisions_made'],
            'phase_distribution': self._get_phase_distribution()
        }
    
    def _get_phase_distribution(self) -> Dict[str, int]:
        """Get entry count per phase"""
        distribution = {}
        
        for phase in ConversationPhase:
            count = len([e for e in self.discourse.conversation.entries 
                        if e.phase == phase])
            if count > 0:
                distribution[phase.value] = count
        
        return distribution