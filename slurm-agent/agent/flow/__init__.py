"""
agent/flow package — Slurm AgentSystem and supporting primitives.
"""
# Install SDK compatibility patches before anything else imports the SDK.
from . import _handoff_compat  # noqa: F401  (side-effect: monkey-patches agents.util._json)

from .agent import SlurmAgentSystem

__all__ = ["SlurmAgentSystem"]
