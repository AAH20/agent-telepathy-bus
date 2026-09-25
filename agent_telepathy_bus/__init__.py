"""
Agent-Telepathy-Bus: Zero-Token CRDT Shared Memory Mesh for Heterogeneous AI Agent Swarms.
Enables sub-millisecond P2P knowledge convergence across Claude Opus 5.5, GPT-6 Astra, and DeepSeek V4.1-Flash.
"""

from .models import (
    FactType,
    FactEntry,
    CRDTVectorState,
    SyncPacket,
)
from .crdt_mesh import CRDTAgentMeshNode
from .system_prompt_injector import SystemPromptInjector

__version__ = "1.0.0"
__all__ = [
    "FactType",
    "FactEntry",
    "CRDTVectorState",
    "SyncPacket",
    "CRDTAgentMeshNode",
    "SystemPromptInjector",
]
