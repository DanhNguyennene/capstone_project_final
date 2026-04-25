"""
Dynamic tool discovery from the MCP server.

Replaces the old _DANGEROUS_TOOL_SCHEMAS hardcoded dict.  At agent init-time
we contact the MCP server once via JSON-RPC to retrieve the live tool list,
then classify each tool into one of three buckets:

  analysis   — read-only data gathering / web search
  safe       — safe-to-execute actions (no confirmation needed)
  dangerous  — must be queued for user confirmation

Classification is driven by two small config sets below (just names, no schemas).
Schemas are fetched from MCP dynamically, so adding / renaming a tool on the
server side is automatically reflected without touching agent code.
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Set

from mcp import ClientSession
from mcp.client.sse import sse_client

logger = logging.getLogger(__name__)


# ── Classification config ─────────────────────────────────────────────────────
# These are the only "known" values — they're policy labels, not duplicated schemas.

DANGEROUS_TOOL_NAMES: Set[str] = {
    "scancel", "scontrol_hold", "scontrol_release", "scontrol_update", "sbatch",
    "scontrol_requeue",
    "scontrol_suspend", "scontrol_resume_job",
    "srun", "salloc", "sattach", "sbcast",
    "scontrol_reconfigure",
    "sacctmgr_add", "sacctmgr_modify", "sacctmgr_delete",
    "sacctmgr_recalc", "sacctmgr_archive", "sacctmgr_load", "sacctmgr_dump",
    "strigger_set", "strigger_clear",
    # Node and reservation management
    "scontrol_node",
    "scontrol_node_power_down", "scontrol_node_power_up",
    "scontrol_node_features", "scontrol_node_gres", "scontrol_node_weight",
    "scontrol_create_reservation",
    "scontrol_delete_reservation",
    "scontrol_update_reservation",
    # Cluster control
    "scontrol_write_config", "scontrol_setdebug", "scontrol_token", "scontrol_shutdown",
}

ANALYSIS_TOOL_NAMES: Set[str] = {
    "squeue", "sacct", "sinfo", "scontrol_show",
    "sacctmgr_list",  # read-only listing of accounting entities
    "sdiag", "sprio", "sstat", "read_file", "web_search",
    "fetch_web_content",
    # Extended read-only tools
    "sreport",                    # CPU/GPU-hour usage reports
    "scontrol_license",           # software license availability
    "scontrol_reservation_show",  # list/show reservations
    # Additional query/introspection tools
    "sshare",
    "scontrol_show_config", "scontrol_ping", "scontrol_show_topology",
    "scontrol_show_step", "scontrol_show_federation", "scontrol_show_burstbuffer",
    "sinfo_reasons", "sinfo_node",
    "squeue_steps", "squeue_reservation",
    "sprio_weights",
    "strigger_get",
    "scontrol_show_aliases",
    "sacctmgr_show_problems",
    "get_mock_state_snapshot",
}

# Everything else discovered on the MCP server is treated as safe.


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class DiscoveredTool:
    name: str
    description: str
    schema: Dict        # JSON Schema dict from MCP tools/list
    category: str       # "analysis" | "safe" | "dangerous" | "other"


@dataclass
class ToolCatalog:
    """Result returned by discover_tools()."""
    analysis:      List[DiscoveredTool] = field(default_factory=list)
    safe:          List[DiscoveredTool] = field(default_factory=list)
    dangerous:     List[DiscoveredTool] = field(default_factory=list)
    other:         List[DiscoveredTool] = field(default_factory=list)

    # Convenience name sets for MCP tool filters
    @property
    def analysis_names(self) -> Set[str]:
        return {t.name for t in self.analysis}

    @property
    def safe_names(self) -> Set[str]:
        return {t.name for t in self.safe}

    @property
    def dangerous_names(self) -> Set[str]:
        return {t.name for t in self.dangerous}

    def by_name(self, name: str) -> DiscoveredTool | None:
        for bucket in (self.analysis, self.safe, self.dangerous, self.other):
            for tool in bucket:
                if tool.name == name:
                    return tool
        return None


# ── Discovery ─────────────────────────────────────────────────────────────────

async def discover_tools(mcp_url: str) -> ToolCatalog:
    """
    Fetch the live tool list from the MCP server via SSE transport.
    Classify each tool and return a ToolCatalog with live schemas.

    Raises if the MCP server is unreachable.
    """
    base = mcp_url.rstrip("/")
    logger.info(f"Discovering tools from {base}/sse")

    async with sse_client(f"{base}/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_response = await session.list_tools()

    raw_tools = tools_response.tools
    logger.info(f"MCP returned {len(raw_tools)} tools")

    catalog = ToolCatalog()
    for t in raw_tools:
        name   = t.name
        desc   = t.description or ""
        schema = t.inputSchema or {"type": "object", "properties": {}, "required": []}

        if name in DANGEROUS_TOOL_NAMES:
            category = "dangerous"
        elif name in ANALYSIS_TOOL_NAMES:
            category = "analysis"
        else:
            # Heuristic for unknown tools: scan description for danger verbs
            desc_lower = desc.lower()
            danger_verbs = {"cancel", "delete", "remove", "hold", "submit", "modify", "reconfigure", "create"}
            category = "dangerous" if any(v in desc_lower for v in danger_verbs) else "safe"
            if category == "dangerous":
                logger.warning(f"Auto-classified '{name}' as dangerous via description heuristic")

        tool = DiscoveredTool(name=name, description=desc, schema=schema, category=category)
        getattr(catalog, category, catalog.other).append(tool)
        logger.debug(f"  {category:12} {name}")

    logger.info(
        f"Catalog — analysis:{len(catalog.analysis)} safe:{len(catalog.safe)} "
        f"dangerous:{len(catalog.dangerous)} other:{len(catalog.other)}"
    )
    return catalog
