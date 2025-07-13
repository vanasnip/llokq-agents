"""
Command Executor - Handles actual execution of commands with agent context
"""
import subprocess
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from unified.agents import Agent
from unified.core.command_parser import ParsedCommand
from unified.validation import get_command_validator, get_input_validator
from unified.tools import ToolContext, CommandExecutionTool
from unified.agents.discourse import DiscourseContext, discourse_safe


class CommandExecutor:
    """Executes commands with agent-specific context and MCP preferences"""
    
    def __init__(self, working_dir: Optional[Path] = None, discourse_mode: bool = False):
        self.working_dir = working_dir or Path.cwd()
        self.execution_history = []
        self.command_validator = get_command_validator()
        self.input_validator = get_input_validator()
        self.command_tool = CommandExecutionTool()
        self.discourse_mode = discourse_mode
        self.discourse_context = DiscourseContext() if discourse_mode else None
    
    def execute(self, command: ParsedCommand, agents: List[Agent]) -> Dict[str, Any]:
        """Execute a command with agent context and validation"""
        # Validate command
        validation_errors = self._validate_command(command)
        if validation_errors:
            return {
                'status': 'error',
                'message': 'Validation failed',
                'errors': validation_errors
            }
        
        # Build execution context
        context = self._build_context(command, agents)
        
        # Select execution strategy based on command
        if command.base_command == 'code':
            return self._execute_code(context)
        elif command.base_command == 'design':
            return self._execute_design(context)
        elif command.base_command == 'analyze':
            return self._execute_analyze(context)
        elif command.base_command == 'test':
            return self._execute_test(context)
        elif command.base_command == 'deploy':
            return self._execute_deploy(context)
        else:
            return {
                'status': 'error',
                'message': f'No executor for command: {command.base_command}'
            }
    
    def _build_context(self, command: ParsedCommand, agents: List[Agent]) -> Dict[str, Any]:
        """Build execution context from command and agents"""
        context = {
            'command': command.base_command,
            'raw_input': command.raw_input,
            'agents': agents,
            'mcp_preferences': set(),
            'decision_frameworks': [],
            'success_metrics': [],
            'focus_areas': [],
            'discourse_context': self.discourse_context
        }
        
        # Aggregate agent attributes
        for agent in agents:
            context['mcp_preferences'].update(agent.mcp_preferences)
            context['decision_frameworks'].append(agent.decision_framework)
            context['success_metrics'].append(agent.success_metrics)
            context['focus_areas'].extend(agent.focus_areas)
        
        # Convert set to list for JSON serialization
        context['mcp_preferences'] = list(context['mcp_preferences'])
        
        return context
    
    @discourse_safe()
    def _execute_code(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coding tasks with agent guidance"""
        agents = context['agents']
        
        # Build agent-specific prompts
        prompts = []
        for agent in agents:
            prompt = f"""
Acting as {agent.identity}

Core Belief: {agent.core_belief}
Primary Question: {agent.primary_question}
Decision Framework: {agent.decision_framework}

Focus Areas: {', '.join(agent.focus_areas)}
Success Metrics: {agent.success_metrics}
"""
            prompts.append(prompt)
        
        # Prepare MCP server preferences
        mcp_config = self._prepare_mcp_config(context['mcp_preferences'])
        
        result = {
            'status': 'success',
            'command': 'code',
            'agents': [a.name for a in agents],
            'prompts': prompts,
            'mcp_config': mcp_config,
            'message': 'Code execution context prepared'
        }
        
        self.execution_history.append(result)
        return result
    
    @discourse_safe()
    def _execute_design(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute design tasks with agent guidance"""
        agents = context['agents']
        
        # Design-specific execution
        design_context = {
            'design_principles': [],
            'accessibility_requirements': [],
            'visual_guidelines': []
        }
        
        for agent in agents:
            if 'aura' in agent.name:
                design_context['accessibility_requirements'].extend([
                    'WCAG AA compliance',
                    'Keyboard navigation',
                    'Screen reader support'
                ])
            elif 'brand' in agent.name or 'chromatic' in agent.name:
                design_context['visual_guidelines'].extend([
                    'Brand consistency',
                    'Color accessibility',
                    'Cultural sensitivity'
                ])
            elif 'layout' in agent.name:
                design_context['design_principles'].extend([
                    'Mobile-first approach',
                    '8pt grid system',
                    'Information hierarchy'
                ])
        
        result = {
            'status': 'success',
            'command': 'design',
            'agents': [a.name for a in agents],
            'design_context': design_context,
            'message': 'Design execution context prepared'
        }
        
        self.execution_history.append(result)
        return result
    
    @discourse_safe()
    def _execute_analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis tasks with agent guidance"""
        agents = context['agents']
        
        analysis_approaches = []
        for agent in agents:
            analysis_approaches.append({
                'agent': agent.name,
                'approach': agent.problem_solving,
                'focus': agent.focus_areas
            })
        
        result = {
            'status': 'success',
            'command': 'analyze',
            'agents': [a.name for a in agents],
            'analysis_approaches': analysis_approaches,
            'message': 'Analysis execution context prepared'
        }
        
        self.execution_history.append(result)
        return result
    
    @discourse_safe()
    def _execute_test(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute testing tasks with agent guidance"""
        agents = context['agents']
        
        test_strategies = {
            'coverage_targets': [],
            'test_types': [],
            'validation_criteria': []
        }
        
        for agent in agents:
            if 'qa' in agent.name:
                test_strategies['test_types'].extend([
                    'Unit tests',
                    'Integration tests',
                    'E2E tests'
                ])
                test_strategies['coverage_targets'].append('>90% coverage')
            elif 'security' in agent.name:
                test_strategies['test_types'].extend([
                    'Security scanning',
                    'Vulnerability assessment',
                    'Penetration testing'
                ])
            elif 'performance' in agent.name:
                test_strategies['test_types'].extend([
                    'Load testing',
                    'Performance profiling',
                    'Bottleneck analysis'
                ])
        
        result = {
            'status': 'success',
            'command': 'test',
            'agents': [a.name for a in agents],
            'test_strategies': test_strategies,
            'message': 'Test execution context prepared'
        }
        
        self.execution_history.append(result)
        return result
    
    @discourse_safe()
    def _execute_deploy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute deployment tasks with agent guidance"""
        agents = context['agents']
        
        deployment_config = {
            'strategies': [],
            'validations': [],
            'rollback_plan': False
        }
        
        for agent in agents:
            if 'devops' in agent.name:
                deployment_config['strategies'].extend([
                    'Blue-green deployment',
                    'Canary releases',
                    'Infrastructure as Code'
                ])
                deployment_config['rollback_plan'] = True
            elif 'security' in agent.name:
                deployment_config['validations'].extend([
                    'Security scan before deploy',
                    'Secrets management check',
                    'Access control validation'
                ])
        
        result = {
            'status': 'success',
            'command': 'deploy',
            'agents': [a.name for a in agents],
            'deployment_config': deployment_config,
            'message': 'Deployment execution context prepared'
        }
        
        self.execution_history.append(result)
        return result
    
    def _prepare_mcp_config(self, mcp_preferences: List[str]) -> Dict[str, Any]:
        """Prepare MCP server configuration based on agent preferences"""
        mcp_config = {
            'servers': [],
            'priority_order': []
        }
        
        # Parse MCP preferences
        for pref in mcp_preferences:
            # Handle formats like "filesystem(code)" or just "shell"
            if '(' in pref:
                server, context = pref.split('(')
                context = context.rstrip(')')
                mcp_config['servers'].append({
                    'name': server.strip(),
                    'context': context,
                    'priority': 'primary' if 'primary' in pref else 'secondary'
                })
            else:
                mcp_config['servers'].append({
                    'name': pref.strip(),
                    'context': 'general',
                    'priority': 'standard'
                })
        
        # Set priority order
        mcp_config['priority_order'] = [
            s['name'] for s in sorted(
                mcp_config['servers'], 
                key=lambda x: 0 if x['priority'] == 'primary' else 1
            )
        ]
        
        return mcp_config
    
    def _validate_command(self, command: ParsedCommand) -> List[str]:
        """Validate command for safety and correctness"""
        errors = []
        
        # Validate base command
        if command.base_command not in self.ALLOWED_COMMANDS:
            errors.append(f"Unknown command: {command.base_command}")
        
        # Validate agent names
        for agent_name in command.agents:
            if not re.match(r'^[a-z][a-z0-9_-]*$', agent_name):
                errors.append(f"Invalid agent name format: {agent_name}")
        
        # Validate options based on command type
        if command.base_command == 'code' and command.options:
            # Validate code-specific options
            if 'file' in command.options:
                file_errors = self.input_validator.validate('file_path', {'path': command.options['file']})
                errors.extend(file_errors)
        
        elif command.base_command == 'deploy' and command.options:
            # Validate deployment options
            if 'environment' in command.options:
                allowed_envs = ['development', 'staging', 'production']
                if command.options['environment'] not in allowed_envs:
                    errors.append(f"Invalid environment: {command.options['environment']}")
        
        return errors
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get history of executed commands"""
        return self.execution_history
    
    # Class-level allowed commands
    ALLOWED_COMMANDS = {
        'code', 'design', 'analyze', 'test', 'deploy',
        'phase', 'workflow', 'team', 'agent'
    }

# Mark mutating methods for discourse mode
CommandExecutor._execute_code._mutates = True
CommandExecutor._execute_test._mutates = True  
CommandExecutor._execute_deploy._mutates = True