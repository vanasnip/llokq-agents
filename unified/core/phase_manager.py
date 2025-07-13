"""
Phase Manager - Manages D3P phases and transitions
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import yaml
import uuid
from unified.agents import Agent, AgentManager
from unified.core.event_bus import get_event_bus, Event, EventType
from unified.core.schema_version import get_schema_validator, SchemaType


@dataclass
class Phase:
    """Represents a D3P phase"""
    number: int
    name: str
    description: str
    agents: List[str]
    lead_agent: str
    outputs: List[str]
    validation_criteria: List[str]
    parallel: bool = False
    
    def is_complete(self, artifacts: Dict[str, bool]) -> bool:
        """Check if phase is complete based on required outputs"""
        return all(artifacts.get(output, False) for output in self.outputs)


class PhaseManager:
    """Manages D3P phases and orchestrates transitions"""
    
    def __init__(self, agent_manager: AgentManager, config_path: Optional[Path] = None):
        self.agent_manager = agent_manager
        self.config_path = config_path or Path.home() / ".claude" / "d3p" / "phases.yml"
        self.phases: Dict[int, Phase] = {}
        self.current_phase: int = 1
        self.phase_artifacts: Dict[int, Dict[str, bool]] = {}
        self.event_bus = get_event_bus()
        self.schema_validator = get_schema_validator()
        self._load_phases()
        self._publish_phase_started()
    
    def _load_phases(self) -> None:
        """Load phase definitions from configuration with schema migration"""
        if not self.config_path.exists():
            self._create_default_d3p_phases()
        
        # Load with schema migration
        config = self.schema_validator.load_config_with_migration(
            self.config_path,
            SchemaType.PHASE
        )
        
        for phase_num, phase_data in config.get('phases', {}).items():
            self.phases[int(phase_num)] = Phase(
                number=int(phase_num),
                name=phase_data['name'],
                description=phase_data.get('description', ''),
                agents=phase_data.get('agents', []),
                lead_agent=phase_data.get('lead', ''),
                outputs=phase_data.get('outputs', []),
                validation_criteria=phase_data.get('validation', []),
                parallel=phase_data.get('parallel', False)
            )
    
    def _create_default_d3p_phases(self) -> None:
        """Create default D3P phases configuration"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        default_phases = {
            'phases': {
                1: {
                    'name': 'Vision & Requirements',
                    'description': 'Establish project vision and gather requirements',
                    'agents': ['requirements', 'architect'],
                    'lead': 'requirements',
                    'outputs': ['requirements.md', 'ambiguities.md', 'success_metrics.md'],
                    'validation': ['Requirements documented', 'Ambiguities resolved', 'Success metrics defined']
                },
                2: {
                    'name': 'Architecture & Planning',
                    'description': 'Design system architecture and technical approach',
                    'agents': ['architect'],
                    'lead': 'architect',
                    'outputs': ['architecture.md', 'technical_plan.md', 'api_design.md'],
                    'validation': ['Architecture documented', 'Technology choices justified', 'API contracts defined']
                },
                3: {
                    'name': 'Design System',
                    'description': 'Create UI/UX design system and components',
                    'agents': ['brand', 'layout', 'motion'],
                    'lead': 'layout',
                    'parallel': True,
                    'outputs': ['design_system.md', 'components.md', 'style_guide.md'],
                    'validation': ['Design system complete', 'Components documented', 'Accessibility verified']
                },
                4: {
                    'name': 'Development Setup',
                    'description': 'Set up development environment and CI/CD',
                    'agents': ['architect', 'devops'],
                    'lead': 'devops',
                    'outputs': ['dev_environment.md', 'ci_pipeline.yml', 'deployment_config.yml'],
                    'validation': ['Dev environment functional', 'CI/CD operational', 'Tests passing']
                },
                5: {
                    'name': 'Core Implementation',
                    'description': 'Implement core features and functionality',
                    'agents': ['backend', 'frontend'],
                    'lead': 'backend',
                    'parallel': True,
                    'outputs': ['api/', 'ui/', 'tests/'],
                    'validation': ['Core features implemented', 'Unit tests passing', 'Integration tests passing']
                },
                6: {
                    'name': 'Testing & Security',
                    'description': 'Comprehensive testing and security audit',
                    'agents': ['qa', 'security'],
                    'lead': 'qa',
                    'parallel': True,
                    'outputs': ['test_report.md', 'security_audit.md', 'performance_report.md'],
                    'validation': ['All tests passing', 'Security vulnerabilities addressed', 'Performance acceptable']
                },
                7: {
                    'name': 'Refinement',
                    'description': 'Polish, optimize, and refine the system',
                    'agents': ['frontend', 'backend', 'performance'],
                    'lead': 'performance',
                    'outputs': ['optimization_report.md', 'final_benchmarks.md'],
                    'validation': ['Performance optimized', 'UX polished', 'Code refactored']
                },
                8: {
                    'name': 'Deployment Preparation',
                    'description': 'Prepare for production deployment',
                    'agents': ['devops', 'security'],
                    'lead': 'devops',
                    'outputs': ['deployment_checklist.md', 'runbook.md', 'monitoring_setup.md'],
                    'validation': ['Deployment ready', 'Monitoring configured', 'Rollback plan defined']
                },
                9: {
                    'name': 'Production Release',
                    'description': 'Deploy to production environment',
                    'agents': ['devops'],
                    'lead': 'devops',
                    'outputs': ['deployment_log.md', 'release_notes.md'],
                    'validation': ['Successfully deployed', 'Health checks passing', 'No critical issues']
                },
                10: {
                    'name': 'Documentation & Handoff',
                    'description': 'Complete documentation and knowledge transfer',
                    'agents': ['architect', 'qa'],
                    'lead': 'architect',
                    'outputs': ['user_guide.md', 'admin_guide.md', 'api_docs.md', 'architecture_docs.md'],
                    'validation': ['Documentation complete', 'Guides reviewed', 'Knowledge transferred']
                }
            }
        }
        
        # Add schema version
        default_phases = self.schema_validator.add_version_to_config(
            default_phases,
            SchemaType.PHASE
        )
        
        with open(self.config_path, 'w') as f:
            yaml.dump(default_phases, f, default_flow_style=False)
    
    def get_current_phase(self) -> Phase:
        """Get the current active phase"""
        return self.phases.get(self.current_phase)
    
    def advance_phase(self) -> bool:
        """Move to the next phase if current is complete"""
        current = self.get_current_phase()
        if not current:
            return False
        
        # Check if current phase is complete
        artifacts = self.phase_artifacts.get(self.current_phase, {})
        if not current.is_complete(artifacts):
            return False
        
        # Move to next phase
        if self.current_phase < 10:
            old_phase = self.current_phase
            self.current_phase += 1
            
            # Publish phase completed event
            self._publish_phase_completed(old_phase)
            
            self._activate_phase_agents()
            
            # Publish phase started event
            self._publish_phase_started()
            
            return True
        
        return False
    
    def goto_phase(self, phase_number: int) -> bool:
        """Jump to a specific phase"""
        if phase_number not in self.phases:
            return False
        
        old_phase = self.current_phase
        self.current_phase = phase_number
        
        # Publish phase change event
        self.event_bus.publish(Event(
            type=EventType.PHASE_CHANGED,
            data={
                "from_phase": old_phase,
                "to_phase": phase_number,
                "phase_name": self.phases[phase_number].name
            },
            source="PhaseManager",
            correlation_id=str(uuid.uuid4())
        ))
        
        self._activate_phase_agents()
        self._publish_phase_started()
        return True
    
    def _activate_phase_agents(self) -> None:
        """Activate agents for the current phase"""
        current = self.get_current_phase()
        if not current:
            return
        
        # Deactivate all agents first
        for agent_name in list(self.agent_manager.active_agents):
            self.agent_manager.deactivate_agent(agent_name)
        
        # Activate phase agents
        for agent_name in current.agents:
            try:
                self.agent_manager.activate_agent(agent_name)
            except ValueError:
                print(f"Warning: Agent '{agent_name}' not found for phase {current.number}")
    
    def mark_output_complete(self, output: str) -> None:
        """Mark a phase output as complete"""
        if self.current_phase not in self.phase_artifacts:
            self.phase_artifacts[self.current_phase] = {}
        
        self.phase_artifacts[self.current_phase][output] = True
        
        # Check if phase is now complete
        current = self.get_current_phase()
        if current and current.is_complete(self.phase_artifacts[self.current_phase]):
            # Phase just completed
            self.event_bus.publish(Event(
                type=EventType.PHASE_COMPLETED,
                data={
                    "phase": self.current_phase,
                    "phase_name": current.name,
                    "outputs": list(self.phase_artifacts[self.current_phase].keys())
                },
                source="PhaseManager"
            ))
    
    def get_phase_status(self) -> Dict[str, Any]:
        """Get detailed status of current phase"""
        current = self.get_current_phase()
        if not current:
            return {'error': 'No current phase'}
        
        artifacts = self.phase_artifacts.get(self.current_phase, {})
        
        return {
            'phase': self.current_phase,
            'name': current.name,
            'description': current.description,
            'lead_agent': current.lead_agent,
            'active_agents': list(self.agent_manager.active_agents),
            'outputs': {
                output: artifacts.get(output, False)
                for output in current.outputs
            },
            'completion': sum(artifacts.get(o, False) for o in current.outputs) / len(current.outputs) * 100
        }
    
    def validate_phase(self) -> Dict[str, bool]:
        """Validate current phase completion"""
        current = self.get_current_phase()
        if not current:
            return {}
        
        validation_results = {}
        artifacts = self.phase_artifacts.get(self.current_phase, {})
        
        # Check outputs
        for output in current.outputs:
            validation_results[f"Output: {output}"] = artifacts.get(output, False)
        
        # Check validation criteria
        for criteria in current.validation_criteria:
            # This would be expanded with actual validation logic
            validation_results[criteria] = True  # Placeholder
        
        return validation_results
    
    def _publish_phase_started(self) -> None:
        """Publish phase started event"""
        current = self.get_current_phase()
        if current:
            self.event_bus.publish(Event(
                type=EventType.PHASE_STARTED,
                data={
                    "phase": self.current_phase,
                    "phase_name": current.name,
                    "lead_agent": current.lead_agent,
                    "agents": current.agents,
                    "parallel": current.parallel
                },
                source="PhaseManager",
                correlation_id=str(uuid.uuid4())
            ))
    
    def _publish_phase_completed(self, phase_number: int) -> None:
        """Publish phase completed event"""
        phase = self.phases.get(phase_number)
        if phase:
            self.event_bus.publish(Event(
                type=EventType.PHASE_COMPLETED,
                data={
                    "phase": phase_number,
                    "phase_name": phase.name,
                    "outputs": list(self.phase_artifacts.get(phase_number, {}).keys())
                },
                source="PhaseManager",
                correlation_id=str(uuid.uuid4())
            ))