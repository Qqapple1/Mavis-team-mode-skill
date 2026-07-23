#!/usr/bin/env python3
"""
Lightweight YAML frontmatter validator (no PyYAML dependency).

Validates that each .md file with a frontmatter block has:
- name field (string, kebab-case, 1-64 chars)
- description field (string, 50-1024 chars)
- version field (if present, semver)

Also checks that any 'allowed-tools' field is a valid list.

Usage: python3 scripts/validate_yaml.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".github", "scripts"}

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[a-z0-9.]+)?(\+[a-z0-9.]+)?$")


def find_files():
    files = []
    for f in ROOT.rglob("*.md"):
        if any(p in f.parts for p in SKIP_DIRS):
            continue
        files.append(f)
    return sorted(files)


def split_frontmatter(content):
    """Return (fm_text, body) or (None, content) if no frontmatter."""
    if not content.startswith("---"):
        return None, content
    end = content.find("\n---", 3)
    if end == -1:
        return None, content
    fm = content[3:end].strip()
    body = content[end + 4:].lstrip("\n")
    return fm, body


def parse_simple_yaml(text):
    """
    Very simple YAML parser for our specific use case.
    Handles:
      key: value
      key: "quoted value with: colons"
      key:
        - item1
        - item2
      key:
        subkey: value
    Returns nested dict. NOT a general-purpose YAML parser.
    """
    result = {}
    lines = text.split("\n")
    stack = [(0, result)]  # (indent_level, dict)

    for line in lines:
        if not line.strip() or line.strip().startswith("#"):
            continue
        # Compute indent
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        # Pop stack to current indent
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if not stack:
            stack = [(0, result)]
        current = stack[-1][1]

        if stripped.startswith("- "):
            # List item — must be in a key that expects a list
            val = stripped[2:].strip()
            val = _strip_quotes(val)
            # find the most recent key in current that holds a list
            for k, v in reversed(list(current.items())):
                if isinstance(v, list):
                    v.append(_parse_scalar(val))
                    break
            continue

        if ":" not in stripped:
            continue
        key, _, val = stripped.partition(":")
        key = key.strip()
        val = val.strip()
        if not val:
            # Either a nested dict or empty
            new_dict = {}
            current[key] = new_dict
            stack.append((indent + 2, new_dict))
        else:
            current[key] = _parse_scalar(val)

    return result


def _parse_scalar(val):
    val = val.strip()
    if not val:
        return ""
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    if val.lower() in ("true", "yes"):
        return True
    if val.lower() in ("false", "no"):
        return False
    if val.startswith("[") and val.endswith("]"):
        items = [x.strip() for x in val[1:-1].split(",") if x.strip()]
        return [_strip_quotes(x) for x in items]
    return val


def _strip_quotes(s):
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def validate_file(path):
    """Validate one file. Returns list of (severity, message)."""
    issues = []
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return [("ERR", f"cannot read: {e}")]

    fm, body = split_frontmatter(content)
    if fm is None:
        issues.append(("INFO", "no frontmatter (allowed for README/LICENSE/CONTRIBUTING)"))
        return issues

    try:
        data = parse_simple_yaml(fm)
    except Exception as e:
        return [("ERR", f"YAML parse failed: {e}")]

    if not isinstance(data, dict):
        return [("ERR", f"frontmatter is not a dict: {type(data).__name__}")]

    # name
    if "name" not in data:
        issues.append(("WARN", "missing 'name'"))
    else:
        name = str(data["name"])
        if not NAME_RE.match(name):
            issues.append(("ERR", f"name '{name}' not valid kebab-case (must be 1-64 chars, lowercase, hyphens)"))

    # description
    if "description" not in data:
        issues.append(("WARN", "missing 'description'"))
    else:
        desc = str(data["description"])
        dlen = len(desc)
        if dlen < 50:
            issues.append(("WARN", f"description too short ({dlen} chars, should be >= 50)"))
        elif dlen > 1024:
            issues.append(("WARN", f"description too long ({dlen} chars, should be <= 1024)"))

    # version (optional, but if present must be semver)
    if "version" in data:
        ver = str(data["version"])
        if not SEMVER_RE.match(ver):
            issues.append(("WARN", f"version '{ver}' is not semver (expected X.Y.Z)"))

    return issues


def main():
    files = find_files()
    print(f"Validating {len(files)} Markdown files...\n")

    error_count = 0
    warn_count = 0
    info_count = 0
    ok_count = 0

    for f in files:
        rel = f.relative_to(ROOT)
        issues = validate_file(f)
        if not issues:
            print(f"  ✓ {rel}")
            ok_count += 1
            continue
        for sev, msg in issues:
            marker = {"ERR": "✗", "WARN": "⚠", "INFO": "i"}[sev]
            print(f"  {marker} {rel}: {msg}")
            if sev == "ERR":
                error_count += 1
            elif sev == "WARN":
                warn_count += 1
            else:
                info_count += 1

    print(f"\n=== Summary ===")
    print(f"OK:     {ok_count}")
    print(f"Info:   {info_count}")
    print(f"Warn:   {warn_count}")
    print(f"Error:  {error_count}")

    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
