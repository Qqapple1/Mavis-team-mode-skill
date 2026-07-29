# Encoding Guidelines for TeamForge

This is the **single source of truth** for non-ASCII text handling, ANSI output,
and encoding-related rules. All worker agents reference this file instead of
duplicating the same rules inline.

---

## Core rules

### R1: JSON serialization must use `ensure_ascii=False`

Python's `json.dumps()` defaults to `ensure_ascii=True`, which escapes all
non-ASCII characters as `\uXXXX`. This silently breaks any downstream code that
searches, reads, or matches against the original Unicode strings.

```python
# WRONG (Chinese becomes \u4e2d\u6587 on disk)
lines.append(f"{key}: {json.dumps(value)}")

# RIGHT
lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
```

Applies to: YAML, Markdown frontmatter, JSON configs, log files, any
human-readable file that will be read back by humans or by code doing
string matching.

### R2: File I/O must use `encoding="utf-8"`

Never rely on the system default encoding. Always pass `encoding="utf-8"`
explicitly when reading or writing text files.

```python
# WRONG
content = open("file.txt").read()
open("file.txt", "w").write(text)

# RIGHT
content = open("file.txt", encoding="utf-8").read()
with open("file.txt", "w", encoding="utf-8") as f:
    f.write(text)
```

### R3: CLI tools must support `--no-color` or `NO_COLOR=1`

ANSI color codes break test assertions (exact-match and substring). Every CLI
tool that produces colored output must provide a way to disable it.

**Convention**: honor the `NO_COLOR=1` environment variable (cross-tool standard,
see https://no-color.org) and/or accept a `--no-color` flag.

Implementation (5 lines):

```python
import os, sys

def color(s, code):
    if "--no-color" in sys.argv or "NO_COLOR" in os.environ:
        return s
    return f"\x1b[{code}m{s}\x1b[0m"
```

Popular libraries like `rich`, `click`, and `colorama` already honor `NO_COLOR`
— check before writing your own.

### R4: Tests must strip ANSI escapes before asserting on CLI output

When testing a CLI that emits ANSI-colored output, always strip escapes before
assertions. Prefer passing `--no-color` or setting `NO_COLOR=1`. If neither is
available, strip:

```python
import re

ANSI = re.compile(r'\x1b\[[0-9;]*m')
output = ANSI.sub('', subprocess.run(cmd, capture_output=True, text=True).stdout)
assert "勿施于人" in output
```

### R5: Self-check for non-ASCII round-trip

After writing a file that must preserve non-ASCII content, verify:

```python
content = open(file, encoding='utf-8').read()
if '技术' not in content:
    raise RuntimeError('Non-ASCII round-trip failed')
```

### R6: When fixing bugs, preserve non-ASCII handling

If existing code uses `ensure_ascii=False` / `encoding="utf-8"`, do not remove
or "simplify" it. A missing `ensure_ascii=False` is itself a common bug
(1-line fix: add the parameter).

---

## Common failure modes

| Symptom | Likely root cause | Typical fix |
|---|---|---|
| `KeyError` on Chinese key lookup | `ensure_ascii=True` default in `json.dumps()` | Add `ensure_ascii=False` (1 line) |
| `UnicodeDecodeError` on file read | Missing `encoding="utf-8"` | Add `encoding="utf-8"` (1 line) |
| ANSI test false-negative | Output wrapped in `\x1b[...m` | Add `--no-color` flag or strip in test |
| Chinese content invisible to `grep`/search | Escaped as `\uXXXX` by `json.dumps()` | Add `ensure_ascii=False` |
| Exact-match assertion fails on CLI output | Hidden ANSI codes in string | Strip ANSI or use `--no-color` |

---

## 数据库编码规范

如果任务涉及数据库存储，**必须**在 CONTRACT 中明确指定数据库连接字符集：

- **MySQL/MariaDB**: `charset=utf8mb4`（支持 emoji）
- **PostgreSQL**: `client_encoding='UTF8'`
- **SQLite**: 默认 UTF-8，无需额外配置
- **MongoDB**: 默认 UTF-8，无需额外配置

**示例**（MySQL 连接字符串）：
```python
# ✅ 正确
conn = mysql.connector.connect(host="localhost", database="mydb", charset="utf8mb4")

# ❌ 错误（依赖服务端默认配置，可能不是 UTF-8）
conn = mysql.connector.connect(host="localhost", database="mydb")
```

**CONTRACT 模板**：如果任务涉及数据库，CONTRACT 中必须包含：
```markdown
## 数据库规范
- 连接字符集: utf8mb4
- 表字符集: utf8mb4_unicode_ci
- 字段编码: UTF-8
```
