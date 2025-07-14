"""
Context management for workflow execution
"""
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class SharedContext:
    """
    Manages shared state within a workflow execution
    """
    
    def __init__(self):
        self.artifacts = {}
        self.insights = {}
        self.constraints = []
        self.agent_states = {}
        self._access_log = []
        self._expiry_times = {}
        
    def add_artifact(self, key: str, value: Any, producer: str, 
                    consumers: List[str] = None, ttl_minutes: int = 60):
        """
        Add an artifact to shared context
        
        Args:
            key: Unique identifier for the artifact
            value: The artifact value
            producer: Agent that produced the artifact
            consumers: List of agents allowed to consume (None = all)
            ttl_minutes: Time to live in minutes
        """
        self.artifacts[key] = {
            'value': value,
            'producer': producer,
            'consumers': consumers or ['*'],
            'created_at': datetime.now(),
            'accessed_by': [],
            'access_count': 0
        }
        
        # Set expiry time
        self._expiry_times[key] = datetime.now() + timedelta(minutes=ttl_minutes)
        
        logger.info(f"Added artifact '{key}' from {producer}")
        
    def get_artifact(self, key: str, consumer: str) -> Optional[Any]:
        """
        Retrieve artifact with access control
        
        Args:
            key: Artifact identifier
            consumer: Agent requesting access
            
        Returns:
            Artifact value or None if not found/not authorized
        """
        # Check if artifact exists
        if key not in self.artifacts:
            logger.warning(f"Artifact '{key}' not found for {consumer}")
            return None
            
        # Check if expired
        if key in self._expiry_times and datetime.now() > self._expiry_times[key]:
            logger.info(f"Artifact '{key}' has expired")
            del self.artifacts[key]
            del self._expiry_times[key]
            return None
            
        artifact = self.artifacts[key]
        
        # Check access permissions
        if '*' not in artifact['consumers'] and consumer not in artifact['consumers']:
            logger.warning(f"Agent {consumer} not authorized for artifact '{key}'")
            raise PermissionError(f"Agent {consumer} not authorized for {key}")
            
        # Log access
        artifact['accessed_by'].append({
            'agent': consumer,
            'timestamp': datetime.now()
        })
        artifact['access_count'] += 1
        
        self._access_log.append({
            'artifact': key,
            'consumer': consumer,
            'timestamp': datetime.now(),
            'action': 'read'
        })
        
        return artifact['value']
        
    def update_artifact(self, key: str, value: Any, updater: str):
        """Update an existing artifact"""
        if key not in self.artifacts:
            raise KeyError(f"Artifact '{key}' not found")
            
        artifact = self.artifacts[key]
        
        # Check if updater has permission (must be producer or in consumers)
        if updater != artifact['producer'] and '*' not in artifact['consumers'] and updater not in artifact['consumers']:
            raise PermissionError(f"Agent {updater} not authorized to update {key}")
            
        # Update value
        artifact['value'] = value
        artifact['updated_at'] = datetime.now()
        artifact['updated_by'] = updater
        
        logger.info(f"Updated artifact '{key}' by {updater}")
        
    def add_insight(self, agent: str, insight: str, related_artifacts: List[str] = None):
        """
        Add an insight discovered by an agent
        
        Args:
            agent: Agent that discovered the insight
            insight: Description of the insight
            related_artifacts: List of artifact keys this insight relates to
        """
        insight_id = f"insight_{len(self.insights)}"
        
        self.insights[insight_id] = {
            'agent': agent,
            'insight': insight,
            'related_artifacts': related_artifacts or [],
            'timestamp': datetime.now()
        }
        
        logger.info(f"Added insight from {agent}: {insight[:50]}...")
        
    def add_constraint(self, constraint: str, source: str):
        """Add a constraint discovered during workflow execution"""
        self.constraints.append({
            'constraint': constraint,
            'source': source,
            'timestamp': datetime.now()
        })
        
    def get_agent_state(self, agent: str) -> Dict[str, Any]:
        """Get or create agent-specific state"""
        if agent not in self.agent_states:
            self.agent_states[agent] = {}
        return self.agent_states[agent]
        
    def set_agent_state(self, agent: str, state: Dict[str, Any]):
        """Set agent-specific state"""
        self.agent_states[agent] = state
        
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the context"""
        return {
            'artifacts_count': len(self.artifacts),
            'insights_count': len(self.insights),
            'constraints_count': len(self.constraints),
            'active_agents': list(self.agent_states.keys()),
            'total_accesses': sum(a['access_count'] for a in self.artifacts.values()),
            'artifacts': {
                k: {
                    'producer': v['producer'],
                    'consumers': v['consumers'],
                    'access_count': v['access_count']
                }
                for k, v in self.artifacts.items()
            }
        }
        
    def cleanup_expired(self):
        """Remove expired artifacts"""
        current_time = datetime.now()
        expired_keys = [
            key for key, expiry in self._expiry_times.items()
            if current_time > expiry
        ]
        
        for key in expired_keys:
            del self.artifacts[key]
            del self._expiry_times[key]
            logger.info(f"Cleaned up expired artifact: {key}")
            
    def export(self) -> Dict[str, Any]:
        """Export context for persistence or debugging"""
        return {
            'artifacts': {
                k: {
                    **v,
                    'created_at': v['created_at'].isoformat(),
                    'accessed_by': [
                        {**access, 'timestamp': access['timestamp'].isoformat()}
                        for access in v['accessed_by']
                    ]
                }
                for k, v in self.artifacts.items()
            },
            'insights': {
                k: {**v, 'timestamp': v['timestamp'].isoformat()}
                for k, v in self.insights.items()
            },
            'constraints': [
                {**c, 'timestamp': c['timestamp'].isoformat()}
                for c in self.constraints
            ],
            'agent_states': self.agent_states
        }


class ContextManager:
    """
    Manages contexts across multiple workflow executions
    """
    
    def __init__(self):
        self.workflow_contexts = {}
        self.global_insights = []
        self._cleanup_interval = timedelta(hours=1)
        self._last_cleanup = datetime.now()
        
    def get_context(self, workflow_id: str) -> SharedContext:
        """Get or create context for a workflow"""
        if workflow_id not in self.workflow_contexts:
            self.workflow_contexts[workflow_id] = SharedContext()
        return self.workflow_contexts[workflow_id]
        
    def share_across_workflows(self, source_workflow: str, target_workflow: str,
                             artifact_key: str, agent: str):
        """Share an artifact from one workflow to another"""
        source_context = self.get_context(source_workflow)
        target_context = self.get_context(target_workflow)
        
        # Get artifact from source
        artifact_value = source_context.get_artifact(artifact_key, agent)
        if artifact_value is None:
            raise ValueError(f"Artifact '{artifact_key}' not found in source workflow")
            
        # Add to target
        target_context.add_artifact(
            f"shared_{artifact_key}",
            artifact_value,
            producer=f"{source_workflow}:{agent}",
            consumers=['*']  # Allow all agents in target workflow
        )
        
    def add_global_insight(self, workflow_id: str, agent: str, insight: str):
        """Add an insight that's valuable across workflows"""
        self.global_insights.append({
            'workflow_id': workflow_id,
            'agent': agent,
            'insight': insight,
            'timestamp': datetime.now()
        })
        
    def find_similar_contexts(self, workflow_id: str, similarity_threshold: float = 0.7) -> List[str]:
        """Find workflows with similar contexts (for reuse)"""
        current_context = self.get_context(workflow_id)
        current_artifacts = set(current_context.artifacts.keys())
        
        similar_workflows = []
        
        for other_id, other_context in self.workflow_contexts.items():
            if other_id == workflow_id:
                continue
                
            other_artifacts = set(other_context.artifacts.keys())
            
            # Simple Jaccard similarity
            intersection = len(current_artifacts & other_artifacts)
            union = len(current_artifacts | other_artifacts)
            
            if union > 0:
                similarity = intersection / union
                if similarity >= similarity_threshold:
                    similar_workflows.append({
                        'workflow_id': other_id,
                        'similarity': similarity,
                        'shared_artifacts': list(current_artifacts & other_artifacts)
                    })
                    
        return similar_workflows
        
    def cleanup(self):
        """Periodic cleanup of expired contexts"""
        current_time = datetime.now()
        
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
            
        # Cleanup expired artifacts in all contexts
        for context in self.workflow_contexts.values():
            context.cleanup_expired()
            
        # Remove old global insights
        cutoff_time = current_time - timedelta(days=7)
        self.global_insights = [
            insight for insight in self.global_insights
            if insight['timestamp'] > cutoff_time
        ]
        
        self._last_cleanup = current_time
        logger.info("Completed context cleanup")
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics across all contexts"""
        total_artifacts = sum(
            len(ctx.artifacts) for ctx in self.workflow_contexts.values()
        )
        total_insights = sum(
            len(ctx.insights) for ctx in self.workflow_contexts.values()
        )
        
        return {
            'active_workflows': len(self.workflow_contexts),
            'total_artifacts': total_artifacts,
            'total_insights': total_insights,
            'global_insights': len(self.global_insights),
            'contexts_summary': {
                wf_id: ctx.get_summary()
                for wf_id, ctx in self.workflow_contexts.items()
            }
        }