#!/usr/bin/env python3
"""
TeamForge CONTRACT 验证脚本 (AST 解析)
用法: python validate_contract_ast.py <file.py> <func1> <func2> ...
示例: python validate_contract_ast.py src/main.py scan_file scan_directory detect_language
"""

import ast
import sys
import os

def validate_functions(file_path: str, expected_funcs: list[str]) -> dict:
    """验证 Python 文件中是否存在指定的函数。"""
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
    if len(sys.argv) < 3:
        print("用法: python validate_contract_ast.py <file.py> <func1> [func2] ...")
        sys.exit(1)

    file_path = sys.argv[1]
    expected_funcs = sys.argv[2:]

    result = validate_functions(file_path, expected_funcs)

    if result["error"]:
        print(f"❌ 错误: {result['error']}")
        sys.exit(1)

    print(f"📄 文件: {result['file']}")

    for func in result["found"]:
        print(f"  ✅ {func}")

    for func in result["missing"]:
        print(f"  ❌ {func} (未找到)")

    if result["missing"]:
        print(f"\n⚠️  缺失 {len(result['missing'])} 个函数")
        sys.exit(1)
    else:
        print(f"\n✅ 全部 {len(result['found'])} 个函数验证通过")
        sys.exit(0)

if __name__ == "__main__":
    main()
