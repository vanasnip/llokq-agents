"""
MCP Server for DiscourseAgent - Provides read-only tools for Claude Code
"""
from typing import Dict, List, Any, Optional
import json
from pathlib import Path
from unified.agents.discourse import (
    DiscourseAgent,
    DiscourseCommandParser,
    ConversationPhase,
    EntryType
)
from unified.agents.schema import Agent, AgentCategory, RiskProfile


class DiscourseMCPServer:
    """
    MCP Server that exposes discourse functionality as tools for Claude Code.
    All operations are read-only to maintain safety.
    """
    
    def __init__(self):
        # Create discourse agent instance
        discourse_config = self._load_discourse_config()
        self.agent = Agent(**discourse_config)
        self.discourse = DiscourseAgent(self.agent)
        self.parser = DiscourseCommandParser()
        
    def _load_discourse_config(self) -> Dict[str, Any]:
        """Load discourse agent configuration"""
        # This would normally load from agents.yml, but we'll use defaults for now
        return {
            'name': 'discourse',
            'command': '--discourse',
            'category': AgentCategory.DISCOURSE,
            'identity': 'Conversational Facilitator & Knowledge Architect',
            'core_belief': 'Understanding emerges through structured dialogue',
            'primary_question': 'What insights should we preserve from this discussion?',
            'decision_framework': 'capture > execute | clarity > action | memory > immediacy',
            'risk_profile': RiskProfile.ZERO_TOLERANCE,
            'success_metrics': '100% read-only operations | Clear decision capture',
            'communication_style': 'Socratic, reflective, structured',
            'problem_solving': 'Explore > Synthesize > Archive > Reference',
            'mcp_preferences': ['memory', 'filesystem(read-only)'],
            'focus_areas': [
                'Conversation facilitation',
                'Knowledge extraction',
                'Decision documentation',
                'Memory organization'
            ]
        }
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools for MCP"""
        return [
            {
                'name': 'discourse_discuss',
                'description': 'Start or continue a discussion on a topic',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'topic': {
                            'type': 'string',
                            'description': 'The topic to discuss'
                        }
                    },
                    'required': ['topic']
                }
            },
            {
                'name': 'discourse_question',
                'description': 'Add a question to explore',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'question': {
                            'type': 'string',
                            'description': 'The question to add'
                        },
                        'category': {
                            'type': 'string',
                            'description': 'Category for the question',
                            'default': 'exploration'
                        }
                    },
                    'required': ['question']
                }
            },
            {
                'name': 'discourse_insight',
                'description': 'Record an insight or observation',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'insight': {
                            'type': 'string',
                            'description': 'The insight to record'
                        },
                        'references': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'File references related to the insight'
                        }
                    },
                    'required': ['insight']
                }
            },
            {
                'name': 'discourse_decide',
                'description': 'Make and record a decision',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'decision': {
                            'type': 'string',
                            'description': 'The decision to record'
                        },
                        'rationale': {
                            'type': 'string',
                            'description': 'Rationale for the decision'
                        }
                    },
                    'required': ['decision']
                }
            },
            {
                'name': 'discourse_phase',
                'description': 'Transition conversation phase',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'phase': {
                            'type': 'string',
                            'description': 'Phase to transition to',
                            'enum': ['exploration', 'analysis', 'synthesis', 'decision', 'archive']
                        }
                    },
                    'required': ['phase']
                }
            },
            {
                'name': 'discourse_search',
                'description': 'Search conversation entries',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'query': {
                            'type': 'string',
                            'description': 'Search query'
                        },
                        'type': {
                            'type': 'string',
                            'description': 'Entry type to filter',
                            'enum': ['question', 'insight', 'decision', 'summary', 'reference', 'plan', 'memory']
                        },
                        'category': {
                            'type': 'string',
                            'description': 'Category to filter'
                        }
                    }
                }
            },
            {
                'name': 'discourse_context',
                'description': 'Get current conversation context',
                'parameters': {
                    'type': 'object',
                    'properties': {}
                }
            },
            {
                'name': 'discourse_summarize',
                'description': 'Generate conversation summary',
                'parameters': {
                    'type': 'object',
                    'properties': {}
                }
            },
            {
                'name': 'discourse_outline',
                'description': 'Generate conversation outline',
                'parameters': {
                    'type': 'object',
                    'properties': {}
                }
            },
            {
                'name': 'discourse_export',
                'description': 'Export conversation for archival',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'format': {
                            'type': 'string',
                            'description': 'Export format',
                            'enum': ['markdown', 'json', 'both'],
                            'default': 'markdown'
                        }
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a discourse tool"""
        try:
            if tool_name == 'discourse_discuss':
                return self.discourse.execute('discuss', {'topic': parameters['topic']})
                
            elif tool_name == 'discourse_question':
                return self.discourse.execute('question', {
                    'question': parameters['question'],
                    'category': parameters.get('category', 'exploration')
                })
                
            elif tool_name == 'discourse_insight':
                return self.discourse.execute('insight', {
                    'insight': parameters['insight'],
                    'references': parameters.get('references', [])
                })
                
            elif tool_name == 'discourse_decide':
                options = {'decision': parameters['decision']}
                if 'rationale' in parameters:
                    options['context'] = {'rationale': parameters['rationale']}
                return self.discourse.execute('decide', options)
                
            elif tool_name == 'discourse_phase':
                return self.discourse.execute('phase', {'phase': parameters['phase']})
                
            elif tool_name == 'discourse_search':
                return self.discourse.execute('search', parameters)
                
            elif tool_name == 'discourse_context':
                return self.discourse.execute('context', {})
                
            elif tool_name == 'discourse_summarize':
                return self.discourse.execute('summarize', {})
                
            elif tool_name == 'discourse_outline':
                return self.discourse.execute('outline', {})
                
            elif tool_name == 'discourse_export':
                result = self.discourse.execute('archive', {})
                
                # Format based on requested format
                if result['status'] == 'success':
                    archive_data = self.discourse.conversation.prepare_archive()
                    format_type = parameters.get('format', 'markdown')
                    
                    if format_type == 'markdown':
                        return {
                            'status': 'success',
                            'format': 'markdown',
                            'content': archive_data['markdown'],
                            'filename': archive_data['filename']
                        }
                    elif format_type == 'json':
                        return {
                            'status': 'success',
                            'format': 'json',
                            'content': json.dumps(archive_data['data'], indent=2),
                            'filename': archive_data['json_filename']
                        }
                    else:  # both
                        return {
                            'status': 'success',
                            'format': 'both',
                            'markdown': archive_data['markdown'],
                            'json': json.dumps(archive_data['data'], indent=2),
                            'markdown_filename': archive_data['filename'],
                            'json_filename': archive_data['json_filename']
                        }
                
                return result
                
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown tool: {tool_name}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Tool execution failed: {str(e)}'
            }
    
    def get_prompts(self) -> Dict[str, str]:
        """Get system prompts for discourse mode"""
        return {
            'system': """You are operating in Discourse Mode - a read-only conversational facilitator.

Your role is to:
1. Facilitate structured discussions
2. Capture insights and decisions
3. Organize knowledge without modifying any files
4. Help users think through problems systematically

You have access to discourse tools for:
- Starting discussions on topics
- Recording questions, insights, and decisions
- Transitioning through conversation phases
- Searching and organizing conversation history
- Exporting conversations for archival

All file system operations are READ-ONLY. You cannot:
- Create or modify files
- Execute code
- Run commands that change system state

Use the discourse tools to maintain a structured conversation that captures valuable insights.""",
            
            'assistant': """I'm now in Discourse Mode - a read-only conversational facilitator. I'll help you explore ideas, capture insights, and make decisions without modifying any files.

Our conversation will progress through phases:
- **Exploration**: Asking questions and gathering context
- **Analysis**: Breaking down the problem
- **Synthesis**: Combining insights
- **Decision**: Making choices
- **Archive**: Preserving knowledge

What would you like to discuss?"""
        }
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """Get MCP configuration for Claude Code"""
        return {
            'name': 'discourse',
            'version': '1.0.0',
            'description': 'Read-only conversational facilitator for structured discussions',
            'tools': self.get_tools(),
            'prompts': self.get_prompts(),
            'capabilities': {
                'read_only': True,
                'conversation_tracking': True,
                'decision_capture': True,
                'knowledge_export': True
            }
        }