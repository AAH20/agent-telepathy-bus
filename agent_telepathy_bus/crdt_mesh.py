"""
CRDT Shared Memory Mesh Engine for Agent-Telepathy-Bus.
Provides conflict-free Lamport LWW synchronization across distributed agent peers.
"""

import copy
import time
from typing import Dict, List, Optional, Tuple, Any
from .models import FactType, FactEntry, SyncPacket, CRDTVectorState


class CRDTAgentMeshNode:
    """A peer node in the agent swarm CRDT shared memory network."""

    def __init__(self, peer_id: str, agent_model: str = "Claude Opus 5.5"):
        self.peer_id = peer_id
        self.agent_model = agent_model
        self.lamport_clock: int = 0
        self.state = CRDTVectorState(peer_id=peer_id, agent_model=agent_model)
        self.state.vector_clock[self.peer_id] = 0

    def set_fact(self, key: str, fact_type: FactType, value: Any) -> FactEntry:
        """Sets or updates an environmental fact discovered by this agent."""
        self.lamport_clock += 1
        self.state.vector_clock[self.peer_id] = self.lamport_clock

        entry = FactEntry(
            key=key,
            fact_type=fact_type,
            value=value,
            origin_peer_id=self.peer_id,
            lamport_clock=self.lamport_clock,
            timestamp=time.time()
        )
        self.state.facts[key] = entry
        return entry

    def delete_fact(self, key: str) -> Optional[FactEntry]:
        """Tombstones a fact across the swarm mesh."""
        if key not in self.state.facts:
            return None

        self.lamport_clock += 1
        self.state.vector_clock[self.peer_id] = self.lamport_clock

        entry = self.state.facts[key]
        entry.is_deleted = True
        entry.lamport_clock = self.lamport_clock
        entry.timestamp = time.time()
        return entry

    def generate_sync_packet(self, remote_vector: Optional[Dict[str, int]] = None) -> SyncPacket:
        """Emits delta facts needed by peers based on vector clock differences."""
        remote_vector = remote_vector or {}
        deltas: List[FactEntry] = []

        for key, entry in self.state.facts.items():
            last_known = remote_vector.get(entry.origin_peer_id, 0)
            if entry.lamport_clock > last_known:
                deltas.append(copy.deepcopy(entry))

        return SyncPacket(
            sender_peer_id=self.peer_id,
            vector_clock=copy.deepcopy(self.state.vector_clock),
            delta_facts=deltas
        )

    def merge_sync_packet(self, packet: SyncPacket) -> int:
        """
        Merges an incoming sync packet using Last-Write-Wins (LWW) conflict resolution.
        Returns number of facts updated or added.
        """
        updates_applied = 0

        # Update local Lamport clock
        sender_clock = packet.vector_clock.get(packet.sender_peer_id, 0)
        self.lamport_clock = max(self.lamport_clock, sender_clock) + 1
        self.state.vector_clock[self.peer_id] = self.lamport_clock

        # Merge peer vector clock entries
        for peer, clk in packet.vector_clock.items():
            self.state.vector_clock[peer] = max(self.state.vector_clock.get(peer, 0), clk)

        # Merge facts with LWW rules
        for incoming in packet.delta_facts:
            local = self.state.facts.get(incoming.key)

            if not local:
                # New fact
                self.state.facts[incoming.key] = incoming
                updates_applied += 1
            else:
                # Conflict resolution: Higher Lamport clock wins.
                # If equal, deterministic tie-break on origin_peer_id string
                if incoming.lamport_clock > local.lamport_clock:
                    self.state.facts[incoming.key] = incoming
                    updates_applied += 1
                elif incoming.lamport_clock == local.lamport_clock:
                    if incoming.origin_peer_id > local.origin_peer_id:
                        self.state.facts[incoming.key] = incoming
                        updates_applied += 1

        return updates_applied

    def get_active_facts(self) -> Dict[str, Any]:
        """Returns non-tombstoned facts currently converged in this node."""
        return {
            k: entry.value
            for k, entry in self.state.facts.items()
            if not entry.is_deleted
        }
