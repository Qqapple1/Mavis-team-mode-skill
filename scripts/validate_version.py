#!/usr/bin/env python3
"""版本一致性检查脚本"""
import re, sys, os

def get_version_from_yaml(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.match(r'version:\s*(\S+)', line.strip())
            if m:
                return m.group(1)
    return None

def main():
    expected = sys.argv[1] if len(sys.argv) > 1 else "3.8.0"
    files = ["SKILL.md", "agents/leader.md", "agents/verifier.md"]
    errors = []

    for f in files:
        if not os.path.exists(f):
            errors.append(f"❌ {f}: 文件不存在")
            continue
        ver = get_version_from_yaml(f)
        if ver != expected:
            errors.append(f"❌ {f}: 版本 {ver} != {expected}")
        else:
            print(f"✅ {f}: {ver}")

    # Check all worker files
    import glob
    for f in glob.glob("agents/worker-*.md"):
        ver = get_version_from_yaml(f)
        if ver != expected:
            errors.append(f"❌ {f}: 版本 {ver} != {expected}")

    if errors:
        for e in errors:
            print(e)
        sys.exit(1)
    print(f"\n✅ 所有文件版本一致: {expected}")

if __name__ == "__main__":
    main()
