#!/usr/bin/env python3
"""
Estimate token savings from Mavis Team Mode skill.

This script measures the byte/character count of:
1. The skill itself (SKILL.md + agents/ + examples/) — what Zcode loads
2. An equivalent "no-skill" baseline (full team plan embedded in main context)

Approximation: 1 token ≈ 4 characters (English text average).
For mixed CJK content, we use a separate heuristic.

This is NOT a perfect token count (no BPE encoding) but gives a useful
relative comparison.

Usage:
    python3 scripts/benchmark_tokens.py
    python3 scripts/benchmark_tokens.py --json   # machine-readable output
"""
import argparse
import json
import os
import sys
from pathlib import Path


# Heuristic:
# - ASCII text: 1 token per ~4 characters
# - CJK: 1 token per ~1.5 characters (each ideogram roughly 1 token)
def estimate_tokens(text: str) -> int:
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    cjk_chars = sum(1 for c in text if ord(c) >= 0x4E00 and ord(c) <= 0x9FFF)
    other = len(text) - ascii_chars - cjk_chars
    return int(ascii_chars / 4) + int(cjk_chars / 1.5) + int(other / 4)


def collect_files(base: Path, patterns: list, exclude: list) -> list:
    files = []
    for p in patterns:
        for f in base.glob(p):
            if any(ex in str(f) for ex in exclude):
                continue
            if f.is_file():
                files.append(f)
    return files


def measure_skill(skill_dir: Path) -> dict:
    """Measure the size of the skill itself."""
    components = {
        "SKILL.md": list(skill_dir.glob("SKILL.md")),
        "agents/": list((skill_dir / "agents").glob("*.md")),
        "examples/": list((skill_dir / "examples").glob("*.md")),
        "references/": list((skill_dir / "references").glob("*.md")),
    }
    result = {"components": {}, "total_bytes": 0, "total_tokens": 0}
    for name, files in components.items():
        size = sum(f.stat().st_size for f in files if f.exists())
        text = "".join(f.read_text(encoding="utf-8") for f in files if f.exists())
        tokens = estimate_tokens(text)
        result["components"][name] = {
            "files": len(files),
            "bytes": size,
            "tokens": tokens,
        }
        result["total_bytes"] += size
        result["total_tokens"] += tokens
    return result


def measure_baseline() -> dict:
    """What would the user have without the skill?

    Baseline: a typical Leader prompt for a complex task, written inline.
    Estimated:
    - 1 system message explaining team mode: ~600 tokens
    - 1 full Team Plan with 4 subtasks × 200 tokens: 800 tokens
    - 4 sub-agent prompts × 300 tokens: 1200 tokens
    - Integration/verify instructions: ~400 tokens
    - Total: ~3000 tokens in main context
    """
    return {
        "name": "inline_team_plan (no skill)",
        "total_tokens": 3000,
        "components": {
            "system_msg_explaining_team_mode": 600,
            "team_plan_4_subtasks": 800,
            "4_subagent_prompts": 1200,
            "integrate_and_verify_instructions": 400,
        }
    }


def measure_eager_load(skill_dir: Path) -> dict:
    """Worst case: load everything at once (no progressive disclosure)."""
    files = []
    for pattern in ["**/*.md", "**/*.py", "**/*.sh", "**/*.html"]:
        for f in skill_dir.glob(pattern):
            if ".git" in f.parts or "__pycache__" in f.parts:
                continue
            files.append(f)
    text = "".join(f.read_text(encoding="utf-8") for f in files)
    return {
        "name": "eager_load (load all files)",
        "total_tokens": estimate_tokens(text),
        "components": {"all_skill_files": len(files)},
    }


def measure_progressive_load(skill_dir: Path) -> dict:
    """Realistic: SKILL.md loaded, then only the agents/examples used.

    For a typical complex task with 3 subtasks, the Leader reads:
    - SKILL.md (~600 tokens, loaded on first invoke)
    - agents/leader.md (already in SKILL.md cross-refs, ~300 tokens if not)
    - 2-3 example files (loaded for inspiration, ~200 tokens each)
    - 1-2 agent templates (worker-coder.md, worker-reviewer.md, ~250 each)
    """
    skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    leader_md = (skill_dir / "agents" / "leader.md").read_text(encoding="utf-8")
    # Pick 1-2 examples and 2 worker templates
    example = (skill_dir / "examples" / "refactor-large-module.md").read_text(encoding="utf-8")
    worker_coder = (skill_dir / "agents" / "worker-coder.md").read_text(encoding="utf-8")
    worker_reviewer = (skill_dir / "agents" / "worker-reviewer.md").read_text(encoding="utf-8")
    verifier = (skill_dir / "agents" / "verifier.md").read_text(encoding="utf-8")

    combined = skill_md + leader_md + example + worker_coder + worker_reviewer + verifier
    return {
        "name": "progressive_load (typical complex task)",
        "total_tokens": estimate_tokens(combined),
        "components": {
            "SKILL.md": estimate_tokens(skill_md),
            "agents/leader.md": estimate_tokens(leader_md),
            "examples/refactor-large-module.md": estimate_tokens(example),
            "agents/worker-coder.md": estimate_tokens(worker_coder),
            "agents/worker-reviewer.md": estimate_tokens(worker_reviewer),
            "agents/verifier.md": estimate_tokens(verifier),
        }
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", default=os.getcwd(),
                        help="Skill root directory (default: cwd)")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON only")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    if not (skill_dir / "SKILL.md").exists():
        print(f"Error: SKILL.md not found in {skill_dir}", file=sys.stderr)
        return 1

    skill = measure_skill(skill_dir)
    baseline = measure_baseline()
    eager = measure_eager_load(skill_dir)
    progressive = measure_progressive_load(skill_dir)

    if args.json:
        result = {
            "skill_total_tokens": skill["total_tokens"],
            "skill_total_bytes": skill["total_bytes"],
            "baseline": baseline,
            "eager_load": eager,
            "progressive_load": progressive,
            "savings": {
                "vs_baseline": f"{(1 - progressive['total_tokens'] / baseline['total_tokens']) * 100:.1f}%",
                "vs_eager_load": f"{(1 - progressive['total_tokens'] / eager['total_tokens']) * 100:.1f}%",
            }
        }
        print(json.dumps(result, indent=2))
        return 0

    # Human-friendly output
    print("=" * 60)
    print("  Mavis Team Mode — Token Cost Analysis")
    print("=" * 60)
    print()

    print(f"Skill bundle (everything in repo):")
    print(f"  Files: {sum(c['files'] for c in skill['components'].values())}")
    print(f"  Bytes: {skill['total_bytes']:,}")
    print(f"  Tokens (estimated): {skill['total_tokens']:,}")
    print()

    print("Component breakdown:")
    for name, c in skill["components"].items():
        if c["files"] > 0:
            print(f"  {name:30s}  {c['files']:3d} files  {c['tokens']:5,} tokens")
    print()

    print("Comparison scenarios:")
    print(f"  1. Inline team plan (no skill, baseline):")
    print(f"     ~{baseline['total_tokens']:,} tokens in main context")
    print()
    print(f"  2. Eager load (load entire skill on invoke):")
    print(f"     {eager['total_tokens']:,} tokens")
    print()
    print(f"  3. Progressive load (SKILL.md + only used files):")
    print(f"     {progressive['total_tokens']:,} tokens")
    print()
    print(f"     Sub-components:")
    for name, t in progressive["components"].items():
        print(f"       {name:40s}  {t:5,} tokens")
    print()

    print("Savings (progressive vs other modes):")
    s1 = (1 - progressive["total_tokens"] / baseline["total_tokens"]) * 100
    s2 = (1 - progressive["total_tokens"] / eager["total_tokens"]) * 100
    print(f"  vs inline baseline:  {s1:+.1f}%  ({progressive['total_tokens']:,} vs {baseline['total_tokens']:,})")
    print(f"  vs eager load:      {s2:+.1f}%  ({progressive['total_tokens']:,} vs {eager['total_tokens']:,})")
    print()
    print("=" * 60)
    print("  Disclaimer: token estimates are heuristic (~4 chars/token)")
    print("  Real BPE tokens vary. Use for relative comparison only.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
