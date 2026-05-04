"""
Skill system for the Slurm agent.

Skills are markdown files in the skills/ directory that teach the agent
how to perform complex multi-step investigations.  Each skill describes
when to use it, what steps to follow, and what output format to produce.

Directory layout:
  skills/          — shared read-only skills (loaded by Observer by default)
  skills/observer/ — Observer-only analysis/investigation skills
  skills/arhive/   — legacy shared runbooks (kept under existing repo spelling)
  skills/operator/ — Operator-only write-action skills

Provides:
  - load_skills(dirs)           — read all .md files from a list of dirs
  - load_observer_skills()      — skills/ + skills/observer/ + skills/arhive/
  - load_operator_skills()      — skills/operator/ only
"""
import logging
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)

SKILLS_DIR = Path(__file__).parent.parent / "skills"
ARCHIVE_SKILLS_DIR = SKILLS_DIR / "arhive"  # legacy path in repo (intentional spelling)
SLURM_KNOWLEDGE_DIR = SKILLS_DIR / "slurm_knowledge"
OBSERVER_SKILLS_DIRS = [SKILLS_DIR, SKILLS_DIR / "observer", ARCHIVE_SKILLS_DIR]
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


def load_slurm_docs() -> dict[str, str]:
    """Load the generated local Slurm documentation corpus recursively."""
    docs: dict[str, str] = {}
    if not SLURM_KNOWLEDGE_DIR.exists():
        logger.info("Slurm docs corpus not found: %s", SLURM_KNOWLEDGE_DIR)
        return docs

    for file_path in sorted(SLURM_KNOWLEDGE_DIR.rglob("*.md")):
        if file_path.name == "SLURM_DOCS_INDEX.md":
            continue
        try:
            content = file_path.read_text(encoding="utf-8").strip()
            if not content:
                continue
            relative_name = file_path.relative_to(SLURM_KNOWLEDGE_DIR).as_posix()
            docs[relative_name] = content
        except Exception as exc:
            logger.error("Failed to load Slurm doc %s: %s", file_path, exc)

    logger.info("Loaded %d local Slurm documentation pages from %s", len(docs), SLURM_KNOWLEDGE_DIR)
    return docs
