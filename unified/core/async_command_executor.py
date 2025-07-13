"""
Async Command Executor - Wraps CommandExecutor for async operations
"""
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from unified.agents import Agent
from unified.core.command_parser import ParsedCommand
from unified.core.command_executor import CommandExecutor
from unified.core.event_bus import get_event_bus, Event, EventType


class AsyncCommandExecutor(CommandExecutor):
    """Async wrapper for CommandExecutor with event integration"""
    
    def __init__(self, working_dir: Optional[Path] = None):
        super().__init__(working_dir)
        self.event_bus = get_event_bus()
        self._running_tasks: Dict[str, asyncio.Task] = {}
    
    async def execute_async(self, command: ParsedCommand, agents: List[Agent]) -> Dict[str, Any]:
        """Execute a command asynchronously with event notifications"""
        # Publish command start event
        correlation_id = f"cmd-{command.base_command}-{id(command)}"
        
        self.event_bus.publish(Event(
            type=EventType.COMMAND_EXECUTED,
            data={
                'command': command.base_command,
                'agents': [a.name for a in agents],
                'status': 'started'
            },
            source='AsyncCommandExecutor',
            correlation_id=correlation_id
        ))
        
        try:
            # Run synchronous execute in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                super().execute,
                command,
                agents
            )
            
            # Publish success event
            self.event_bus.publish(Event(
                type=EventType.COMMAND_EXECUTED,
                data={
                    'command': command.base_command,
                    'agents': [a.name for a in agents],
                    'status': 'completed',
                    'result': result
                },
                source='AsyncCommandExecutor',
                correlation_id=correlation_id
            ))
            
            return result
            
        except Exception as e:
            # Publish error event
            self.event_bus.publish(Event(
                type=EventType.ERROR_OCCURRED,
                data={
                    'command': command.base_command,
                    'agents': [a.name for a in agents],
                    'error': str(e)
                },
                source='AsyncCommandExecutor',
                correlation_id=correlation_id
            ))
            
            return {
                'status': 'error',
                'message': f'Command execution failed: {str(e)}'
            }
    
    async def execute_parallel(self, commands: List[ParsedCommand], agents_list: List[List[Agent]]) -> List[Dict[str, Any]]:
        """Execute multiple commands in parallel"""
        if len(commands) != len(agents_list):
            raise ValueError("Commands and agents lists must have same length")
        
        tasks = []
        for cmd, agents in zip(commands, agents_list):
            task = self.execute_async(cmd, agents)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'status': 'error',
                    'command': commands[i].base_command,
                    'message': str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def execute_with_timeout(self, command: ParsedCommand, agents: List[Agent], timeout: float) -> Dict[str, Any]:
        """Execute command with timeout"""
        try:
            result = await asyncio.wait_for(
                self.execute_async(command, agents),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return {
                'status': 'error',
                'command': command.base_command,
                'message': f'Command timed out after {timeout} seconds'
            }
    
    def start_background_task(self, task_id: str, command: ParsedCommand, agents: List[Agent]) -> None:
        """Start a command execution in the background"""
        if task_id in self._running_tasks:
            raise ValueError(f"Task {task_id} already running")
        
        async def background_execution():
            try:
                await self.execute_async(command, agents)
            finally:
                # Clean up task reference
                self._running_tasks.pop(task_id, None)
        
        task = asyncio.create_task(background_execution())
        self._running_tasks[task_id] = task
    
    def cancel_background_task(self, task_id: str) -> bool:
        """Cancel a background task"""
        task = self._running_tasks.get(task_id)
        if task and not task.done():
            task.cancel()
            return True
        return False
    
    def get_running_tasks(self) -> Dict[str, bool]:
        """Get status of running background tasks"""
        return {
            task_id: not task.done()
            for task_id, task in self._running_tasks.items()
        }