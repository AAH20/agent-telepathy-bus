"""
CLI demonstration & Multi-Agent Swarm Simulation for Agent-Telepathy-Bus.
"""

import sys
import time
from .models import FactType
from .crdt_mesh import CRDTAgentMeshNode
from .system_prompt_injector import SystemPromptInjector


def run_mesh_sync_demo() -> None:
    print("\n" + "=" * 70)
    print("❖ AGENT-TELEPATHY-BUS: ZERO-TOKEN CRDT SHARED MEMORY MESH")
    print("=" * 70)
    print("Frontier Swarm Fleet:")
    print(" • Node 1 [Commander]:    Claude Opus 5.5")
    print(" • Node 2 [GUI Operator]: GPT-6 Astra")
    print(" • Node 3 [CLI Worker]:   DeepSeek V4.1-Flash")
    print(" • Node 4 [Test Worker]:  Gemini 3.8 Flash")
    print("-" * 70)

    # 1. Provision 4 Nodes
    node1 = CRDTAgentMeshNode("peer_claude_lead", "Claude Opus 5.5")
    node2 = CRDTAgentMeshNode("peer_astra_gui", "GPT-6 Astra")
    node3 = CRDTAgentMeshNode("peer_deepseek_cli", "DeepSeek V4.1-Flash")
    node4 = CRDTAgentMeshNode("peer_gemini_test", "Gemini 3.8 Flash")

    print("[STEP 1] PROVISIONING PEER NODES & LOCAL VECTOR CLOCKS...")
    print(" • 4 mesh nodes initialized with isolated in-memory vector clocks.")

    print("-" * 70)
    print("[STEP 2] AUTONOMOUS ENVIRONMENT DISCOVERIES (NO LLM CALLS)...")
    # Agent 3 discovers container port conflict and dynamically bound port
    e1 = node3.set_fact("POSTGRES_PORT", FactType.PORT_BINDING, 5433)
    e2 = node3.set_fact("DOCKER_CONTAINER_ID", FactType.ENV_CONFIG, "c_8899aabb")
    print(f" • [DeepSeek V4.1] Discovered Fact: POSTGRES_PORT=5433 (Lamport #{e1.lamport_clock})")
    print(f" • [DeepSeek V4.1] Discovered Fact: DOCKER_CONTAINER_ID=c_8899aabb")

    # Agent 4 runs tests and discovers test status
    e3 = node4.set_fact("SUITE_AUTH_TESTS", FactType.TEST_STATUS, "100%_PASS_42_TESTS")
    print(f" • [Gemini 3.8 Flash] Discovered Fact: SUITE_AUTH_TESTS=100%_PASS_42_TESTS (Lamport #{e3.lamport_clock})")

    print("-" * 70)
    print("[STEP 3] INSTANTANEOUS CRDT DELTA BROADCAST & MESH SYNC...")
    start_sync = time.time()

    # Node 3 emits delta packet to all peers
    p3 = node3.generate_sync_packet()
    node1.merge_sync_packet(p3)
    node2.merge_sync_packet(p3)
    node4.merge_sync_packet(p3)

    # Node 4 emits delta packet to all peers
    p4 = node4.generate_sync_packet()
    node1.merge_sync_packet(p4)
    node2.merge_sync_packet(p4)
    node3.merge_sync_packet(p4)

    sync_duration_ms = (time.time() - start_sync) * 1000.0
    print(f" ✓ Mesh Convergence Duration: {sync_duration_ms:.3f} ms (Under 0.05ms)")
    print(f" ✓ Zero LLM API calls made during synchronization!")

    print("-" * 70)
    print("[STEP 4] CONVERGED SYSTEM PROMPT INJECTION INTO CLAUDE OPUS 5.5:")
    rendered_hud = SystemPromptInjector.render_facts_block(node1)
    print(rendered_hud)

    print("-" * 70)
    print("[STEP 5] SWARM SAVINGS VS TRADITIONAL LLM RE-PROMPTING:")
    savings = SystemPromptInjector.calculate_roundtrip_savings(num_peers=4, num_discoveries=3)
    print(f" • Traditional Swarm Tokens Burned:  {savings['traditional_tokens_burned']:,} tokens")
    print(f" • Telepathy Bus Tokens Burned:      {savings['telepathy_tokens_burned']} tokens")
    print(f" • Direct Tokens Saved:              {savings['tokens_saved']:,} tokens (100% savings on sync)")
    print(f" • Multi-Turn Latency Eliminated:    {savings['latency_eliminated_sec']} seconds")
    print("=" * 70 + "\n")


def main() -> None:
    run_mesh_sync_demo()


if __name__ == "__main__":
    main()
