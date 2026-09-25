"""
Unit tests for Agent-Telepathy-Bus using standard unittest.
"""

import unittest
from agent_telepathy_bus.models import FactType
from agent_telepathy_bus.crdt_mesh import CRDTAgentMeshNode
from agent_telepathy_bus.system_prompt_injector import SystemPromptInjector


class TestAgentTelepathyBus(unittest.TestCase):
    def test_crdt_set_and_sync_convergence(self):
        nodeA = CRDTAgentMeshNode("peer_A", "Claude Opus 5.5")
        nodeB = CRDTAgentMeshNode("peer_B", "DeepSeek V4.1-Flash")

        # Node A discovers a fact
        nodeA.set_fact("PORT", FactType.PORT_BINDING, 8080)
        self.assertEqual(nodeA.get_active_facts()["PORT"], 8080)
        self.assertNotIn("PORT", nodeB.get_active_facts())

        # Sync packet from A to B
        packet = nodeA.generate_sync_packet()
        updates = nodeB.merge_sync_packet(packet)

        self.assertEqual(updates, 1)
        self.assertEqual(nodeB.get_active_facts()["PORT"], 8080)

    def test_crdt_lww_conflict_resolution(self):
        nodeA = CRDTAgentMeshNode("peer_A", "Claude Opus 5.5")
        nodeB = CRDTAgentMeshNode("peer_B", "DeepSeek V4.1-Flash")

        # Node A sets PORT = 8080 at lamport 1
        nodeA.set_fact("PORT", FactType.PORT_BINDING, 8080)

        # Sync to B
        nodeB.merge_sync_packet(nodeA.generate_sync_packet())

        # Later, Node B discovers PORT is reassigned to 8090 (Lamport clock increments to 3)
        nodeB.set_fact("PORT", FactType.PORT_BINDING, 8090)

        # Sync back to A
        nodeA.merge_sync_packet(nodeB.generate_sync_packet())

        # Both must converge strictly to 8090 (LWW)
        self.assertEqual(nodeA.get_active_facts()["PORT"], 8090)
        self.assertEqual(nodeB.get_active_facts()["PORT"], 8090)

    def test_tombstone_deletion(self):
        nodeA = CRDTAgentMeshNode("peer_A")
        nodeB = CRDTAgentMeshNode("peer_B")

        nodeA.set_fact("TEMP_TOKEN", FactType.ENV_CONFIG, "abc123xyz")
        nodeB.merge_sync_packet(nodeA.generate_sync_packet())
        self.assertIn("TEMP_TOKEN", nodeB.get_active_facts())

        # Delete fact in node A
        nodeA.delete_fact("TEMP_TOKEN")
        self.assertNotIn("TEMP_TOKEN", nodeA.get_active_facts())

        # Sync deletion to B
        nodeB.merge_sync_packet(nodeA.generate_sync_packet())
        self.assertNotIn("TEMP_TOKEN", nodeB.get_active_facts())

    def test_prompt_injector_rendering(self):
        node = CRDTAgentMeshNode("peer_test")
        node.set_fact("DB_URL", FactType.ENV_CONFIG, "postgres://localhost/test")
        rendered = SystemPromptInjector.render_facts_block(node)
        self.assertIn("DB_URL", rendered)
        self.assertIn("postgres://localhost/test", rendered)


if __name__ == "__main__":
    unittest.main()
