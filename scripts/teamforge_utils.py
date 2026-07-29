#!/usr/bin/env python3
"""
TeamForge 跨平台工具函数库
用法:
  python scripts/teamforge_utils.py --count-lines <file>
  python scripts/teamforge_utils.py --check-exists <file1> <file2> ...
  python scripts/teamforge_utils.py --strip-ansi <text>
"""

import sys
import os
import re
import glob as glob_mod

def get_file_lines(filepath: str) -> int:
    """获取文件行数（跨平台）"""
    if not os.path.exists(filepath):
        return -1
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return sum(1 for _ in f)

def strip_ansi(text: str) -> str:
    """去除 ANSI 转义码"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def find_files(pattern: str) -> list:
    """查找匹配模式的文件"""
    return glob_mod.glob(pattern, recursive=True)

def match_role(task_description: str, index_path: str = "agents/ROLE_INDEX.yaml") -> list:
    """根据任务描述匹配最佳角色"""
    import difflib
    if not os.path.exists(index_path):
        return [{"role": "worker-team-member", "score": 0, "reason": "ROLE_INDEX.yaml 不存在"}]

    try:
        import yaml
    except ImportError:
        # 回退到简单关键词匹配
        return _match_role_simple(task_description, index_path)

    with open(index_path, 'r', encoding='utf-8') as f:
        index = yaml.safe_load(f)

    results = []
    task_lower = task_description.lower()

    for role, info in index.items():
        keywords = info.get('keywords', [])
        matches = sum(1 for kw in keywords if kw.lower() in task_lower)
        score = matches / max(len(keywords), 1)
        if score > 0:
            results.append({"role": role, "score": round(score, 2), "matched": [kw for kw in keywords if kw.lower() in task_lower]})

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:3]  # 返回前3个最佳匹配

def _match_role_simple(task_description: str, index_path: str) -> list:
    """简单关键词匹配（不依赖 yaml 库）"""
    results = []
    task_lower = task_description.lower()

    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 简单解析 YAML（每个 role 块）
    import re
    blocks = re.split(r'\n(?=\w)', content)
    for block in blocks:
        lines = block.strip().split('\n')
        if not lines or ':' not in lines[0]:
            continue
        role = lines[0].split(':')[0].strip()
        keywords = []
        for line in lines:
            if 'keywords:' in line:
                kw_part = line.split('[')[1].split(']')[0] if '[' in line else ''
                keywords = [k.strip().strip('"').strip("'") for k in kw_part.split(',')]

        if keywords:
            matches = sum(1 for kw in keywords if kw.lower() in task_lower)
            score = matches / len(keywords)
            if score > 0:
                results.append({"role": role, "score": round(score, 2)})

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:3]

def main():
    if len(sys.argv) < 2:
        print("用法: python teamforge_utils.py --count-lines|--check-exists|--strip-ansi ...")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "--count-lines":
        if len(sys.argv) < 3:
            print("用法: --count-lines <file>")
            sys.exit(1)
        filepath = sys.argv[2]
        lines = get_file_lines(filepath)
        if lines == -1:
            print(f"❌ 文件不存在: {filepath}")
            sys.exit(1)
        print(f"{lines}")

    elif cmd == "--check-exists":
        files = sys.argv[2:]
        all_ok = True
        for f in files:
            if os.path.exists(f):
                size = os.path.getsize(f)
                print(f"  ✅ {f} ({size} bytes)")
            else:
                print(f"  ❌ {f} (不存在)")
                all_ok = False
        sys.exit(0 if all_ok else 1)

    elif cmd == "--strip-ansi":
        text = ' '.join(sys.argv[2:])
        print(strip_ansi(text))

    elif cmd == "--match-role":
        if len(sys.argv) < 3:
            print("用法: --match-role <task_description>")
            sys.exit(1)
        task_desc = ' '.join(sys.argv[2:])
        import json
        results = match_role(task_desc)
        print(json.dumps(results, ensure_ascii=False))

    elif cmd == "--write-state":
        if len(sys.argv) < 6:
            print("用法: --write-state <session_uuid> <wave> <task> <status>")
            sys.exit(1)
        uuid = sys.argv[2]
        wave = sys.argv[3]
        task = sys.argv[4]
        status = sys.argv[5]
        import json as json_mod
        from datetime import datetime
        data = {"ts": datetime.now().isoformat(), "wave": int(wave), "task": task, "status": status}
        final = f".teamforge_state_{uuid}.jsonl"
        tmp = f".teamforge_state_{uuid}.tmp"
        with open(tmp, 'a', encoding='utf-8') as f:
            f.write(json_mod.dumps(data, ensure_ascii=False) + '\n')
        if os.path.exists(final):
            os.replace(tmp, final)
        else:
            os.rename(tmp, final)
        print(f"✅ 状态已写入: {final}")

    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
