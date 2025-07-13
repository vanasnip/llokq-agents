"""
Unified D3P-SuperClaude System
"""

__version__ = "0.1.1"
__author__ = "D3P-SuperClaude Team"
__description__ = "A comprehensive AI agent development system with 15+ specialized agents for software development"

# Make version easily accessible
from . import agents
from . import core
from . import workflows

__all__ = [
    "__version__",
    "agents",
    "core",
    "workflows",
]