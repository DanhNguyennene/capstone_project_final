"""
agent/flow package — Slurm AgentSystem and supporting primitives.
"""
from .agent import SlurmAgentSystem

# Backward-compat alias used by agent/main.py
SlurmMultiAgentSystem = SlurmAgentSystem

__all__ = ["SlurmAgentSystem", "SlurmMultiAgentSystem"]
