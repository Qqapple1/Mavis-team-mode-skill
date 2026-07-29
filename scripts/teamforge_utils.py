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

    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
