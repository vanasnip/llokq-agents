"""
Simple JSON-based conversation storage
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ConversationStore:
    """Simple JSON-based storage for conversations"""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize store with optional base path"""
        if base_path is None:
            # Default to user's home directory
            base_path = Path.home() / ".mcp" / "conversations"
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"ConversationStore initialized at: {self.base_path}")
    
    def save_conversation(self, agent_id: str, conversation: Dict[str, Any]) -> str:
        """
        Save a conversation to JSON file
        
        Args:
            agent_id: The agent that created this conversation
            conversation: The conversation data to save
            
        Returns:
            The filename where the conversation was saved
        """
        # Create agent-specific directory
        agent_dir = self.base_path / agent_id
        agent_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().isoformat().replace(':', '-').replace('.', '-')
        filename = f"{agent_id}_{timestamp}.json"
        filepath = agent_dir / filename
        
        # Add metadata
        conversation['_metadata'] = {
            'agent_id': agent_id,
            'saved_at': datetime.now().isoformat(),
            'filename': filename
        }
        
        # Save to file
        try:
            with open(filepath, 'w') as f:
                json.dump(conversation, f, indent=2, default=str)
            logger.info(f"Saved conversation to: {filepath}")
            return filename
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            raise
    
    def load_conversation(self, agent_id: str, filename: str) -> Dict[str, Any]:
        """
        Load a conversation from JSON file
        
        Args:
            agent_id: The agent that created the conversation
            filename: The filename to load
            
        Returns:
            The conversation data
        """
        filepath = self.base_path / agent_id / filename
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Conversation not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Failed to load conversation: {e}")
            raise
    
    def list_conversations(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all conversations, optionally filtered by agent
        
        Args:
            agent_id: Optional agent ID to filter by
            
        Returns:
            List of conversation metadata
        """
        conversations = []
        
        # Determine which directories to search
        if agent_id:
            search_dirs = [(self.base_path / agent_id, agent_id)]
        else:
            # Search all agent directories
            search_dirs = [(d, d.name) for d in self.base_path.iterdir() if d.is_dir()]
        
        for agent_dir, agent_name in search_dirs:
            if not agent_dir.exists():
                continue
                
            for filepath in agent_dir.glob("*.json"):
                try:
                    # Load just the metadata
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        metadata = data.get('_metadata', {})
                        metadata['agent_id'] = agent_name
                        metadata['filepath'] = str(filepath)
                        metadata['size'] = filepath.stat().st_size
                        conversations.append(metadata)
                except Exception as e:
                    logger.warning(f"Failed to read {filepath}: {e}")
        
        # Sort by saved_at descending (newest first)
        conversations.sort(key=lambda x: x.get('saved_at', ''), reverse=True)
        return conversations
    
    def search_conversations(self, query: str, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search conversations for a query string
        
        Args:
            query: The search query
            agent_id: Optional agent ID to filter by
            
        Returns:
            List of matching conversations with context
        """
        query_lower = query.lower()
        results = []
        
        # Get all conversations
        conversations = self.list_conversations(agent_id)
        
        for conv_meta in conversations:
            try:
                # Load the full conversation
                filepath = Path(conv_meta['filepath'])
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Search in the conversation content
                content_str = json.dumps(data).lower()
                if query_lower in content_str:
                    # Find context around the match
                    idx = content_str.find(query_lower)
                    start = max(0, idx - 100)
                    end = min(len(content_str), idx + 100 + len(query_lower))
                    context = content_str[start:end]
                    
                    results.append({
                        'metadata': conv_meta,
                        'context': f"...{context}...",
                        'match_count': content_str.count(query_lower)
                    })
            except Exception as e:
                logger.warning(f"Failed to search {conv_meta.get('filepath')}: {e}")
        
        # Sort by match count descending
        results.sort(key=lambda x: x['match_count'], reverse=True)
        return results
    
    def get_latest_conversation(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent conversation for an agent
        
        Args:
            agent_id: The agent ID
            
        Returns:
            The latest conversation data or None
        """
        conversations = self.list_conversations(agent_id)
        if not conversations:
            return None
        
        # Get the newest one
        latest = conversations[0]
        filename = latest['filename']
        return self.load_conversation(agent_id, filename)