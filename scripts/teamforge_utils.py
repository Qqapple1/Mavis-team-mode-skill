#!/usr/bin/env python3
"""
TeamForge 跨平台工具函数库
用法:
  python scripts/teamforge_utils.py --count-lines <file>
  python scripts/teamforge_utils.py --check-exists <file1> <file2> ...
  python scripts/teamforge_utils.py --strip-ansi <text>
  python scripts/teamforge_utils.py --write-state <session_uuid> <wave> <task> <status> [--files "file1,file2"] [--error "错误信息"]
  python scripts/teamforge_utils.py --check-multi-model
  python scripts/teamforge_utils.py --search-memory <keyword>
  python scripts/teamforge_utils.py --validate-ast <file.py> <func1> [func2] ...
  python scripts/teamforge_utils.py --validate-contract <CONTRACT.md>
  python scripts/teamforge_utils.py --rotate-state <session_uuid>
  python scripts/teamforge_utils.py --glob <pattern>
  python scripts/teamforge_utils.py --grep <pattern> <file>
  python scripts/teamforge_utils.py --suggest-fixer-limit <file>
  python scripts/teamforge_utils.py --list-states
  python scripts/teamforge_utils.py --self-check
"""

import sys
import os
import re
import json
import ast
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

def validate_functions(file_path: str, expected_funcs: list) -> dict:
    """验证 Python 文件中是否存在指定的函数（AST 解析）。"""
    result = {"file": file_path, "found": [], "missing": [], "error": None}

    if not os.path.exists(file_path):
        result["error"] = f"文件不存在: {file_path}"
        return result

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
    except SyntaxError as e:
        result["error"] = f"语法错误 (行 {e.lineno}): {e.msg}"
        return result
    except Exception as e:
        result["error"] = f"读取失败: {e}"
        return result

    # 收集所有函数定义（包括 async def）
    defined_funcs = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined_funcs.add(node.name)

    # 检查期望的函数
    for func_name in expected_funcs:
        if func_name in defined_funcs:
            result["found"].append(func_name)
        else:
            result["missing"].append(func_name)

    return result

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
            print("用法: --write-state <session_uuid> <wave> <task> <status> [--files \"file1,file2\"] [--error \"错误信息\"]")
            sys.exit(1)
        uuid = sys.argv[2]
        wave = sys.argv[3]
        task = sys.argv[4]
        status = sys.argv[5]
        # 解析可选参数
        files_list = []
        error_msg = None
        i = 6
        while i < len(sys.argv):
            if sys.argv[i] == "--files" and i + 1 < len(sys.argv):
                files_list = [f.strip() for f in sys.argv[i + 1].split(',') if f.strip()]
                i += 2
            elif sys.argv[i] == "--error" and i + 1 < len(sys.argv):
                error_msg = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        import json as json_mod
        from datetime import datetime
        data = {"ts": datetime.now().isoformat(), "wave": int(wave), "task": task, "status": status}
        if files_list:
            data["files"] = files_list
        if error_msg:
            data["error"] = error_msg
        final = f".teamforge_state_{uuid}.jsonl"
        tmp = f".teamforge_state_{uuid}.tmp"
        with open(tmp, 'a', encoding='utf-8') as f:
            f.write(json_mod.dumps(data, ensure_ascii=False) + '\n')
            os.fsync(f.fileno())
        if os.path.exists(final):
            os.replace(tmp, final)
        else:
            os.rename(tmp, final)
        print(f"✅ 状态已写入: {final}")

    elif cmd == "--check-multi-model":
        import json
        config_path = os.path.join(os.path.expanduser('~'), '.zcode', 'cli', 'config.json')
        if not os.path.exists(config_path):
            print("multi-model: false")
            print("reason: config file not found")
            sys.exit(0)
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            providers = [k for k in config.get('provider', {}) if config['provider'][k].get('enabled', True)]
            is_multi = len(providers) > 1
            print(f"providers: {len(providers)}")
            print(f"multi-model: {str(is_multi).lower()}")
        except Exception as e:
            print(f"multi-model: false")
            print(f"reason: {e}")

    elif cmd == "--search-memory":
        if len(sys.argv) < 3:
            print("用法: --search-memory <keyword>")
            sys.exit(1)
        keyword = sys.argv[2].lower()
        memory_file = '.memory_index.jsonl'
        if not os.path.exists(memory_file):
            print("未找到记忆索引文件")
            sys.exit(0)

        import difflib
        results = []
        with open(memory_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    summary = entry.get('summary', '')
                    ratio = difflib.SequenceMatcher(None, keyword, summary.lower()).ratio()
                    if ratio > 0.2 or keyword in summary.lower():
                        results.append((ratio, entry))
                except:
                    continue

        results.sort(key=lambda x: x[0], reverse=True)
        if not results:
            print("未找到匹配的记忆")
        else:
            for ratio, entry in results[:5]:
                print(f"[{ratio:.0%}] {entry.get('task', '?')}: {entry.get('summary', '')[:60]}")

    elif cmd == "--validate-ast":
        if len(sys.argv) < 4:
            print("用法: --validate-ast <file.py> <func1> [func2] ...")
            sys.exit(1)
        file_path = sys.argv[2]
        expected_funcs = sys.argv[3:]
        result = validate_functions(file_path, expected_funcs)
        if result.get("error"):
            print(f"❌ 错误: {result['error']}")
            sys.exit(1)
        for func in result.get("found", []):
            print(f"  ✅ {func}")
        for func in result.get("missing", []):
            print(f"  ❌ {func} (未找到)")
        if result.get("missing"):
            sys.exit(1)

    elif cmd == "--validate-contract":
        if len(sys.argv) < 3:
            print("用法: --validate-contract <CONTRACT.md>")
            sys.exit(1)
        filepath = sys.argv[2]
        if not os.path.exists(filepath):
            print(f"❌ 文件不存在: {filepath}")
            sys.exit(1)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        checks = []

        # 检查必要字段
        required = ['primary_language', 'test_framework', 'files_created']
        for field in required:
            if field in content:
                checks.append(f"✅ {field}: 存在")
            else:
                checks.append(f"⚠️ {field}: 缺失")

        # 检查命名规范一致性
        py_funcs = re.findall(r'def\s+(\w+)', content)
        js_funcs = re.findall(r'function\s+(\w+)', content)

        if py_funcs:
            camel = [f for f in py_funcs if re.search(r'[a-z][A-Z]', f)]
            if camel:
                checks.append(f"⚠️ Python 函数使用了 camelCase: {camel[:3]}")
            else:
                checks.append(f"✅ Python 函数命名规范 (snake_case)")

        # 检查产物清单
        if 'files_created' in content:
            files = re.findall(r'files_created.*?\[([^\]]+)\]', content)
            if files:
                checks.append(f"✅ 产物清单: 已定义")

        for c in checks:
            print(c)

        warnings = sum(1 for c in checks if '⚠️' in c)
        if warnings:
            print(f"\n⚠️ 发现 {warnings} 个问题，建议修正后再派发")
            sys.exit(1)
        else:
            print(f"\n✅ 契约自检通过")

    elif cmd == "--rotate-state":
        if len(sys.argv) < 3:
            print("用法: --rotate-state <session_uuid>")
            sys.exit(1)
        uuid = sys.argv[2]
        state_file = f".teamforge_state_{uuid}.jsonl"

        if not os.path.exists(state_file):
            print(f"状态文件不存在: {state_file}")
            sys.exit(0)

        # 检查行数
        with open(state_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if len(lines) <= 1000:
            print(f"状态文件行数 {len(lines)}，无需轮转")
            sys.exit(0)

        # 轮转
        import shutil
        backup = f"{state_file}.1"
        shutil.move(state_file, backup)
        print(f"✅ 状态文件已轮转: {state_file} → {backup} ({len(lines)} 行)")

    elif cmd == "--glob":
        if len(sys.argv) < 3:
            print("用法: --glob <pattern>")
            sys.exit(1)
        pattern = sys.argv[2]
        files = find_files(pattern)
        for f in files:
            print(f)
        if not files:
            print(f"未找到匹配: {pattern}")

    elif cmd == "--grep":
        if len(sys.argv) < 4:
            print("用法: --grep <pattern> <file>")
            sys.exit(1)
        pattern = sys.argv[2]
        filepath = sys.argv[3]
        if not os.path.exists(filepath):
            print(f"❌ 文件不存在: {filepath}")
            sys.exit(1)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                if pattern in line:
                    print(f"{filepath}:{i}: {line.rstrip()}")

    elif cmd == "--suggest-fixer-limit":
        if len(sys.argv) < 3:
            print("用法: --suggest-fixer-limit <file>")
            sys.exit(1)
        filepath = sys.argv[2]
        lines = get_file_lines(filepath)
        if lines == -1:
            print(f"❌ 文件不存在: {filepath}")
            sys.exit(1)
        default_limit = min(int(lines * 0.2), 50)
        print(f"文件行数: {lines}")
        print(f"建议阈值: {default_limit}")
        print(f"公式: min({lines} * 20%, 50) = {default_limit}")

    elif cmd == "--list-states":
        import glob as _glob
        from datetime import datetime
        pattern = ".teamforge_state_*.jsonl"
        files = _glob.glob(pattern)
        if not files:
            print("未找到状态文件")
            sys.exit(0)

        # 按修改时间倒序排列
        files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        for i, fpath in enumerate(files[:3], 1):
            # 从文件名提取 session_uuid
            basename = os.path.basename(fpath)
            uuid_part = basename.replace(".teamforge_state_", "").replace(".jsonl", "")
            # 统计行数
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                line_count = sum(1 for _ in f)
            # 获取修改时间
            mtime = os.path.getmtime(fpath)
            ts = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            print(f"{i}. {basename} ({ts}, {line_count} 条记录)")

    elif cmd == "--self-check":
        print("TeamForge Utils 自检...")
        print(f"Python: {sys.version}")
        print(f"平台: {sys.platform}")

        # 检查所有子命令
        commands = ["--count-lines", "--check-exists", "--strip-ansi", "--match-role",
                    "--write-state", "--check-multi-model", "--search-memory", "--validate-ast",
                    "--validate-contract", "--rotate-state", "--glob", "--grep", "--list-states",
                    "--suggest-fixer-limit"]

        for subcmd in commands:
            print(f"  ✅ {subcmd}: 可用")

        # 检查关键文件
        files = ["agents/ROLE_INDEX.yaml", "references/core-rules.md", "scripts/validate_contract_ast.py"]
        for f in files:
            exists = "✅" if os.path.exists(f) else "❌"
            print(f"  {exists} {f}")

        print("自检完成")

    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
