"""
Data models and typed schemas for Agent-Telepathy-Bus CRDT shared memory mesh.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import time


class FactType(str, Enum):
    ENV_CONFIG = "env_config"         # e.g., "DATABASE_URL"
    PORT_BINDING = "port_binding"     # e.g., "POSTGRES_PORT=5433"
    TEST_STATUS = "test_status"       # e.g., "auth_suite=PASSED"
    CODE_SYMBOL = "code_symbol"       # e.g., "BillingHandler -> pkg/billing.go"
    ERROR_STATE = "error_state"       # e.g., "Kafka broker 2 partition leader unavail"
    FILE_LOC = "file_loc"             # e.g., "swagger.json -> /api/docs/swagger.json"


@dataclass
class FactEntry:
    key: str
    fact_type: FactType
    value: Any
    origin_peer_id: str
    lamport_clock: int
    timestamp: float = field(default_factory=time.time)
    is_deleted: bool = False


@dataclass
class SyncPacket:
    sender_peer_id: str
    vector_clock: Dict[str, int]
    delta_facts: List[FactEntry]


@dataclass
class CRDTVectorState:
    peer_id: str
    agent_model: str
    vector_clock: Dict[str, int] = field(default_factory=dict)
    facts: Dict[str, FactEntry] = field(default_factory=dict)
