"""
🤖 AGENTIC SLURM SYSTEM - ARCHITECTURE OVERVIEW

This system implements a full agentic AI architecture for Slurm HPC management.

================================================================================
ARCHITECTURE LAYERS
================================================================================

┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                      │
│                    (Natural language requests)                                │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR LAYER                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │ Agentic Planner │  │   ReAct Loop    │  │   Multi-Agent Handoffs      │  │
│  │ (Plan creation) │  │ (Think→Act→Obs) │  │   (Agent transfers)         │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AGENT LAYER                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐│
│  │  Chat Agent  │ │ Slurm Agent  │ │ Executor     │ │ Critic Agent         ││
│  │  (Q&A,       │ │ (Command     │ │ Agent        │ │ (Review,             ││
│  │  Explain)    │ │ Generation)  │ │ (Validate,   │ │ Improve)             ││
│  │              │ │              │ │ Execute)     │ │                      ││
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────────┘│
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TOOL LAYER                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                    OpenAI SDK Integration                                ││
│  │  • chat_structured() - Pydantic structured outputs                       ││
│  │  • chat_with_tools() - Function calling                                  ││
│  │  • beta.chat.completions.parse() - Direct parsing                        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                    Slurm Command Builder                                 ││
│  │  • 12 Pydantic command models (sbatch, squeue, scancel, etc.)           ││
│  │  • compile_to_shell() - Generate bash scripts                            ││
│  │  • validate_sequence() - Check commands                                  ││
│  │  • save_script() - Create executable files                               ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       KNOWLEDGE LAYER                                         │
│  ┌───────────────────┐ ┌──────────────────┐ ┌─────────────────────────────┐ │
│  │ Slurm Outputs     │ │ User Interactions│ │ Execution History           │ │
│  │ (Learn from       │ │ (Preferences,    │ │ (Successful plans,          │ │
│  │ command results)  │ │ patterns)        │ │ failed tasks)               │ │
│  └───────────────────┘ └──────────────────┘ └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

================================================================================
KEY COMPONENTS
================================================================================

1. AGENTIC PLANNER (flow/agentic_planner.py)
   - Creates multi-step plans from user requests
   - Chain-of-Thought reasoning
   - Task dependency management
   - Iterative execution with context passing

2. REACT AGENT (flow/react_agent.py)
   - ReAct loop: Think → Act → Observe
   - Self-correction on failures
   - Multiple action types: explain, generate, validate, execute, review
   - Context accumulation across steps

3. MULTI-AGENT SYSTEM (flow/multi_agent_system.py)
   - OpenAI Swarm pattern for handoffs
   - Specialized agents (Chat, Slurm, Executor, Critic)
   - Dynamic agent switching via transfer functions
   - Knowledge base for learning

4. SLURM STRUCTURED AGENT (flow/slurm_structured_agent.py)
   - Structured output generation using Pydantic
   - 12 command types with validation
   - Shell script compilation

5. OPENAI CLIENT (utils/openai_client.py)
   - Full OpenAI SDK feature support
   - beta.chat.completions.parse() for structured outputs
   - Tool calling, streaming, logprobs

6. COMMAND BUILDER (utils/slurm_commands.py)
   - Pydantic models for all Slurm commands
   - Validation and compilation
   - Executable script generation

================================================================================
USAGE EXAMPLES
================================================================================

# Simple command generation
from flow.slurm_structured_agent import SlurmStructuredAgent
agent = SlurmStructuredAgent(model="qwen3.5:9b")
result = await agent.plan_only("Submit a GPU job with 4 GPUs")

# Full agentic planning
from flow.agentic_planner import AgenticSlurmSystem
system = AgenticSlurmSystem(model="qwen3.5:9b")
await system.run("Set up a distributed training workflow with 2 nodes")

# ReAct loop
from flow.react_agent import FullAgenticSystem
system = FullAgenticSystem(model="qwen3.5:9b")
await system.run_react_loop("Create and validate a GPU job script")

# Multi-agent with handoffs
from flow.multi_agent_system import MultiAgentOrchestrator
orchestrator = MultiAgentOrchestrator()
await orchestrator.run_conversation("Explain GRES and create a GPU job")

================================================================================
SUPPORTED MODELS
================================================================================

✅ qwen3.5:9b - Fast (3-7s), works great with structured outputs
✅ qwen2.5:7b         - Slower (30-60s), works with structured outputs  
❌ gpt-oss:20b        - Does not support structured outputs properly
✅ Azure OpenAI       - Full compatibility

================================================================================
"""

print(__doc__)
