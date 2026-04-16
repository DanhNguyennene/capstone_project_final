"""
Skill system for the Slurm agent.

Skills are markdown files in the skills/ directory that teach the agent
how to perform complex multi-step investigations.  Each skill describes
when to use it, what steps to follow, and what output format to produce.

Directory layout:
  skills/          — shared read-only skills (loaded by Observer by default)
  skills/observer/ — Observer-only analysis/investigation skills
  skills/operator/ — Operator-only write-action skills

Provides:
  - load_skills(dirs)           — read all .md files from a list of dirs
  - load_observer_skills()      — skills/ + skills/observer/
  - load_operator_skills()      — skills/operator/ only
  - format_skills_for_instructions()  — build text block to inject into instructions
"""
import logging
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)

SKILLS_DIR = Path(__file__).parent.parent / "skills"
OBSERVER_SKILLS_DIRS = [SKILLS_DIR, SKILLS_DIR / "observer"]
OPERATOR_SKILLS_DIRS = [SKILLS_DIR / "operator"]


# ── Skill loading ─────────────────────────────────────────────────────────────

def load_skills(dirs: Iterable[Path] | None = None) -> dict[str, str]:
    """Load all .md skill files from *dirs* (default: [SKILLS_DIR]).

    Returns {name: content}.  Later dirs override earlier ones on name collision.
    """
    if dirs is None:
        dirs = [SKILLS_DIR]

    skills: dict[str, str] = {}
    for directory in dirs:
        if not directory.exists():
            logger.debug(f"Skills directory not found (skip): {directory}")
            continue
        for f in sorted(directory.glob("*.md")):
            name = f.stem
            try:
                content = f.read_text(encoding="utf-8").strip()
                if content:
                    skills[name] = content
                    logger.debug(f"Loaded skill: {name} (from {directory.name}/)")
            except Exception as e:
                logger.error(f"Failed to load skill {f}: {e}")

    logger.info(f"Loaded {len(skills)} skills from {[str(d) for d in dirs]}")
    return skills


def load_observer_skills() -> dict[str, str]:
    """Load shared + Observer-specific skills."""
    return load_skills(OBSERVER_SKILLS_DIRS)


def load_operator_skills() -> dict[str, str]:
    """Load Operator-specific write-action skills."""
    return load_skills(OPERATOR_SKILLS_DIRS)


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
