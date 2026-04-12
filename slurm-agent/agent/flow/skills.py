"""
Skill system for the Slurm agent.

Skills are markdown files in the skills/ directory that teach the agent
how to perform complex multi-step investigations.  Each skill describes
when to use it, what steps to follow, and what output format to produce.

In the handoff architecture, skills are embedded directly into the Observer
agent's system prompt — no sub-agent indirection needed.

Provides:
  - load_skills()                     — read all .md files from skills dir
  - format_skills_for_instructions()  — build text block to inject into instructions
"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SKILLS_DIR = Path(__file__).parent.parent / "skills"


# ── Skill loading ─────────────────────────────────────────────────────────────

def load_skills() -> dict[str, str]:
    """Load all .md skill files. Returns {name: content}."""
    skills = {}
    if not SKILLS_DIR.exists():
        logger.warning(f"Skills directory not found: {SKILLS_DIR}")
        return skills

    for f in sorted(SKILLS_DIR.glob("*.md")):
        name = f.stem
        try:
            content = f.read_text(encoding="utf-8").strip()
            if content:
                skills[name] = content
                logger.debug(f"Loaded skill: {name}")
        except Exception as e:
            logger.error(f"Failed to load skill {f}: {e}")

    logger.info(f"Loaded {len(skills)} skills from {SKILLS_DIR}")
    return skills


def _compress_skill(name: str, content: str) -> str:
    """Extract a compact summary from a skill markdown file.

    Pulls the 'When to use' line plus the tool names from the Steps section
    to produce a 1-2 line reference instead of the full multi-paragraph skill.
    """
    import re

    # Extract "When to use" trigger
    trigger = ""
    m = re.search(r"\*\*When to use:\*\*\s*(.+)", content)
    if m:
        trigger = m.group(1).strip()

    # Extract tool calls mentioned in the Steps section (backtick-wrapped names)
    tool_calls = re.findall(r"`(\w+)\([^)]*\)`", content)
    # Deduplicate while preserving order
    seen = set()
    unique_tools = []
    for t in tool_calls:
        if t not in seen:
            seen.add(t)
            unique_tools.append(t)

    tools_str = " → ".join(f"`{t}()`" for t in unique_tools) if unique_tools else ""
    line = f"**{name}**: {trigger}"
    if tools_str:
        line += f"\n  Tools: {tools_str}"
    return line


def format_skills_for_instructions(skills: dict[str, str]) -> str:
    """
    Build a compact skill index for the Observer system prompt.

    With the lookup_skill tool available, the agent can load full skill content
    on demand. The prompt only needs skill names so it knows what's available.

    Returns comma-separated skill names, or empty string if no skills.
    """
    if not skills:
        return ""
    return ", ".join(sorted(skills.keys()))
