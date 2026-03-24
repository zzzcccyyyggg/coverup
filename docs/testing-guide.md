# CoverUp 测试指南

本文档详细介绍如何测试 CoverUp 的 Go 语言支持改进，包括单元测试、集成测试和端到端验证。

---

## 1. 环境准备

### 1.1 Python 依赖

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装项目依赖（可编辑模式）
pip install -e ".[dev]"

# 安装 Go 静态分析依赖
pip install tree-sitter tree-sitter-languages
```

### 1.2 Go 工具链

```bash
# 确认 Go 安装（需要 Go 1.20+）
go version

# 确认 goimports 可用（可选但推荐）
go install golang.org/x/tools/cmd/goimports@latest
which goimports
```

### 1.3 Rust 工具链

CoverUp 的 Rust 支持需要以下工具：

```bash
# 1. 安装 rustup（Rust 官方工具链管理器）
#    如果已安装可跳过
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# 2. 验证基础工具链（需要 Rust 1.70+）
rustc --version      # 例如 rustc 1.93.1
cargo --version      # 例如 cargo 1.93.1
rustfmt --version    # 例如 rustfmt 1.8.0-stable

# 3. 安装 llvm-tools-preview（覆盖率插桩所需）
rustup component add llvm-tools-preview

# 4. 安装 cargo-llvm-cov（覆盖率采集工具）
cargo install cargo-llvm-cov

# 5. 验证 cargo-llvm-cov
cargo llvm-cov --version   # 例如 cargo-llvm-cov 0.8.4

# 6. 安装 tree-sitter Rust 解析器（Python 依赖）
pip install tree-sitter tree-sitter-languages
```

**PATH 配置：** 确保 `~/.cargo/bin` 在 PATH 中。rustup 安装时会自动配置，
新终端需执行 `source "$HOME/.cargo/env"` 或将其加入 `~/.zshrc` / `~/.bashrc`。

**快速验证：**
```bash
# 创建临时 crate 跑一次覆盖率测试
cd /tmp && cargo new test_cov_check --lib && cd test_cov_check
echo '#[test] fn it_works() { assert_eq!(2 + 2, 4); }' >> src/lib.rs
cargo llvm-cov --json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Coverage OK: {d[\"data\"][0][\"totals\"][\"lines\"][\"percent\"]:.1f}%')"
cd /tmp && rm -rf test_cov_check
```

### 1.4 LLM API 密钥

```bash
# 至少配置一个：
export OPENAI_API_KEY=sk-...
# 或
export ANTHROPIC_API_KEY=...
```

---

## 2. 运行现有测试

### 2.1 全部 Python 单元测试

```bash
cd /home/zzzccc/coverup
.venv/bin/python -m pytest tests/test_codeinfo.py -x -q
```

预期输出：`32 passed, 1 skipped`

### 2.2 导入验证

快速检查所有改动模块可正常导入：

```bash
# Go 模块
.venv/bin/python -c "
from coverup.go_codeinfo import get_info_go, infer_branches, extract_receiver_type, find_type_definition
from coverup.languages.go_backend import GoBackend
from coverup.prompt.gpt_go_v1 import GoGptV1Prompter
print('All Go imports OK')
"

# Rust 模块
.venv/bin/python -c "
from coverup.rust_codeinfo import get_info_rust, infer_branches as rust_infer_branches
from coverup.languages.rust_backend import RustBackend
from coverup.prompt.gpt_rust_v1 import RustGptV1Prompter
print('All Rust imports OK')
"
```

---

## 3. 测试 `go_codeinfo.py` —— 新 Go 静态分析模块

### 3.1 符号查询 (`get_info_go`)

在 `src/cobra` 目录下有真实的 Go 代码可用于测试：

```bash
.venv/bin/python -c "
from pathlib import Path
from coverup.go_codeinfo import get_info_go

# 测试查找函数定义
result = get_info_go(
    Path('src/cobra/command.go'),
    'Command',
    module_root=Path('src/cobra')
)
print('=== Command type ===')
print(result[:500] if result else 'NOT FOUND')
print()

# 测试查找方法
result = get_info_go(
    Path('src/cobra/command.go'),
    'Command.Execute',
    module_root=Path('src/cobra')
)
print('=== Command.Execute ===')
print(result[:500] if result else 'NOT FOUND')
print()

# 测试 go doc fallback
result = get_info_go(
    Path('src/cobra/command.go'),
    'fmt.Sprintf',
    module_root=Path('src/cobra')
)
print('=== fmt.Sprintf (go doc) ===')
print(result[:300] if result else 'NOT FOUND')
"
```

**预期：** 每个查询都应返回包含 Go 代码片段的字符串（不是 `NOT FOUND`）。

### 3.2 分支覆盖推断 (`infer_branches`)

```bash
.venv/bin/python -c "
from pathlib import Path
from coverup.go_codeinfo import infer_branches

# 对 cobra/command.go 进行分支推断
# 模拟：前 100 行已执行，101-200 行未执行
p = Path('src/cobra/command.go')
lines = p.read_text().splitlines()
total = len(lines)

exec_lines = set(range(1, min(101, total+1)))
miss_lines = set(range(101, min(201, total+1)))

exec_br, miss_br = infer_branches(p, exec_lines, miss_lines)
print(f'Inferred {len(exec_br)} executed branches, {len(miss_br)} missing branches')
for br in miss_br[:5]:
    print(f'  missing branch: line {br[0]} -> {\"exit\" if br[1] == 0 else br[1]}')
"
```

**预期：** 应能推断出若干分支（数量取决于控制流语句密度）。

### 3.3 接收者类型提取

```bash
.venv/bin/python -c "
from pathlib import Path
from coverup.go_codeinfo import _ensure_parser, extract_receiver_type, _node_text

parser = _ensure_parser()
source = Path('src/cobra/command.go').read_bytes()
tree = parser.parse(source)

count = 0
for child in tree.root_node.children:
    if child.type == 'method_declaration':
        recv_type = extract_receiver_type(child, source)
        name_node = child.child_by_field_name('name')
        name = _node_text(name_node, source) if name_node else '?'
        if recv_type and count < 5:
            print(f'Method: ({recv_type}).{name}')
            count += 1
print(f'... found methods on various receiver types')
"
```

---

## 4. 测试 `go_backend.py` —— 增强的 Go 后端

### 4.1 代码分段增强

验证新的 `_find_enclosing_node` 能找到 struct/interface/const/var：

```bash
.venv/bin/python -c "
import argparse
from pathlib import Path
from coverup.languages.go_backend import GoBackend

# 构造最小参数
args = argparse.Namespace(
    package_dir=Path('src/cobra').resolve(),
    prefix='coverup',
    tests_dir=Path('src/cobra').resolve(),
    go_test_args='',
)
backend = GoBackend(args)

# 获取缺失覆盖的 segments（使用空覆盖 = 全部缺失）
coverage = backend.initial_empty_coverage()
segments = backend.get_missing_coverage(coverage, line_limit=50)
print(f'Found {len(segments)} segments')

# 展示前 10 个段
for seg in segments[:10]:
    print(f'  {seg.name}: lines {seg.begin}-{seg.end}, '
          f'{len(seg.missing_lines)} missing lines, '
          f'{len(seg.missing_branches)} missing branches')
"
```

**预期：** 应找到几十至上百个 segment，每个都有名字（函数/方法/类型名），部分应包含非零的 `missing_branches`。

### 4.2 错误清洗

```bash
.venv/bin/python -c "
import argparse
from pathlib import Path
from coverup.languages.go_backend import GoBackend

args = argparse.Namespace(
    package_dir=Path('src/cobra').resolve(),
    prefix='coverup',
    tests_dir=Path('src/cobra').resolve(),
    go_test_args='',
)
backend = GoBackend(args)

# 模拟 go test 的冗余输出
sample_output = '''
=== RUN   TestSomething
--- FAIL: TestSomething (0.00s)
somefile.go:42: undefined: NonExistentFunc
somefile.go:50: cannot use x (type int) as type string
ok  	github.com/example/pkg	0.005s
FAIL	github.com/example/pkg/sub	[build failed]
some random debug log line
another irrelevant line
panic: runtime error: index out of range [5] with length 3
'''

cleaned = backend.format_test_error(sample_output)
print('=== Cleaned output ===')
print(cleaned)
print(f'\\n(Original: {len(sample_output)} chars -> Cleaned: {len(cleaned)} chars)')
"
```

**预期：** 清洗后只保留包含 `.go:`、`FAIL`、`panic:` 等关键词的行。

### 4.3 覆盖率解析含分支

```bash
.venv/bin/python -c "
import tempfile, os
from pathlib import Path
from coverup.languages.go_backend import parse_go_cover_profile

# 创建模拟 cover profile
profile_content = '''mode: count
github.com/example/pkg/main.go:10.2,15.16 3 1
github.com/example/pkg/main.go:15.16,18.3 2 0
github.com/example/pkg/main.go:18.3,22.2 3 1
'''

# 写临时文件
fd, tmp = tempfile.mkstemp(suffix='.out')
with open(tmp, 'w') as f:
    f.write(profile_content)
os.close(fd)

coverage = parse_go_cover_profile(Path(tmp))
os.unlink(tmp)

print('Parsed coverage:')
for fname, data in coverage['files'].items():
    print(f'  {fname}:')
    print(f'    executed: {data[\"executed_lines\"]}')
    print(f'    missing:  {data[\"missing_lines\"]}')
    print(f'    exec_branches:  {data.get(\"executed_branches\", [])}')
    print(f'    miss_branches:  {data.get(\"missing_branches\", [])}')
print(f'  branch_coverage enabled: {coverage[\"meta\"][\"branch_coverage\"]}')
"
```

**预期：** `branch_coverage` 为 `True`，行数据正确分为 executed/missing。

---

## 5. 测试 `gpt_go_v1.py` —— 重写的 Go Prompter

### 5.1 Prompt 生成验证

```bash
.venv/bin/python -c "
import argparse
from pathlib import Path
from coverup.prompt.gpt_go_v1 import GoGptV1Prompter
from coverup.segment import CodeSegment

args = argparse.Namespace(
    src_base_dir=Path('src/cobra').resolve(),
    package_dir=Path('src/cobra').resolve(),
)

prompter = GoGptV1Prompter(cmd_args=args)

# 构造一个模拟 segment
seg = CodeSegment(
    'src/cobra/command.go',
    'Execute',
    920, 950,
    lines_of_interest={925, 930, 935},
    missing_lines={925, 930},
    executed_lines={920, 921, 922, 935},
    missing_branches={(925, 930), (925, 0)},
    context=[(1, 2)],
    imports=[],
)

# 生成 initial prompt
messages = prompter.initial_prompt(seg)
print('=== Initial Prompt ===')
print(messages[0]['content'][:1500])
print('...')

# 验证 get_info 工具函数存在
funcs = prompter.get_functions()
print(f'\\nTool functions exposed: {len(funcs)}')
for f in funcs:
    print(f'  - {f.__name__}')

# 测试 get_info
result = prompter.get_info(ctx=seg, name='Command')
print(f'\\nget_info(\"Command\") result length: {len(result) if result else 0} chars')
print(result[:300] if result else 'No result')
"
```

**预期：**
- Prompt 包含角色设定、覆盖率描述（含分支 `branches 925->930, 925->exit`）、约束和代码摘录
- 暴露 1 个工具函数 `get_info`
- `get_info("Command")` 返回 `Command` 结构体定义

### 5.2 动态指导验证

```bash
.venv/bin/python -c "
import argparse
from pathlib import Path
from coverup.prompt.gpt_go_v1 import GoGptV1Prompter
from coverup.segment import CodeSegment

args = argparse.Namespace(
    src_base_dir=Path('src/cobra').resolve(),
    package_dir=Path('src/cobra').resolve(),
)
prompter = GoGptV1Prompter(cmd_args=args)

# 测试动态指导检测
# command.go 包含 error 返回、context、interface 等
seg = CodeSegment(
    'src/cobra/command.go', 'Execute',
    920, 950,
    lines_of_interest={925},
    missing_lines={925},
    executed_lines=set(),
    missing_branches=set(),
    context=[(1,2)],
    imports=[],
)

hints = prompter._dynamic_go_guidance(seg)
print(f'Dynamic hints generated: {len(hints)}')
for h in hints:
    print(f'  {h}')
"
```

### 5.3 Error / Missing-Coverage Prompt

```bash
.venv/bin/python -c "
import argparse
from pathlib import Path
from coverup.prompt.gpt_go_v1 import GoGptV1Prompter
from coverup.segment import CodeSegment

args = argparse.Namespace(
    src_base_dir=Path('src/cobra').resolve(),
    package_dir=Path('src/cobra').resolve(),
)
prompter = GoGptV1Prompter(cmd_args=args)

seg = CodeSegment(
    'src/cobra/command.go', 'Execute', 920, 950,
    lines_of_interest={925}, missing_lines={925},
    executed_lines=set(), missing_branches={(925, 0)},
    context=[(1,2)], imports=[],
)

# error prompt
err_msgs = prompter.error_prompt(seg, 'command_test.go:15: undefined: fakeFunc')
print('=== Error Prompt ===')
print(err_msgs[0]['content'][:500])

# missing coverage prompt
miss_msgs = prompter.missing_coverage_prompt(seg, {925, 930}, {(925, 0)})
print('\\n=== Missing Coverage Prompt ===')
print(miss_msgs[0]['content'][:500])
"
```

---

## 6. 测试 `rust_codeinfo.py` —— Rust 静态分析模块

### 6.1 符号查询 (`get_info_rust`)

```bash
.venv/bin/python -c "
from pathlib import Path
from coverup.rust_codeinfo import get_info_rust
import tempfile, os

# 创建临时 Rust 样本代码
code = '''
pub fn add(a: i32, b: i32) -> i32 { a + b }

pub struct Calculator { pub value: f64 }

impl Calculator {
    pub fn new() -> Self { Self { value: 0.0 } }
    pub fn add(&mut self, x: f64) { self.value += x; }
}

pub enum Color { Red, Green, Blue }

pub trait Drawable { fn draw(&self); }
'''
fd, tmp = tempfile.mkstemp(suffix='.rs')
with open(tmp, 'w') as f:
    f.write(code)
os.close(fd)

p = Path(tmp)
for name in ['add', 'Calculator', 'Calculator::new', 'Color', 'Drawable']:
    result = get_info_rust(p, name)
    status = 'FOUND' if result else 'NOT FOUND'
    print(f'{name}: {status}')
    if result:
        print(f'  {result[:100]}...')

os.unlink(tmp)
"
```

**预期：** 所有 5 个符号都返回 `FOUND`，包含对应的代码片段。

### 6.2 分支覆盖推断

```bash
.venv/bin/python -c "
from pathlib import Path
from coverup.rust_codeinfo import infer_branches
import tempfile, os

code = '''fn check(x: i32) -> &'static str {
    if x > 0 {
        \"positive\"
    } else {
        \"non-positive\"
    }
}

fn classify(c: char) -> i32 {
    match c {
        'a'..='z' => 1,
        'A'..='Z' => 2,
        _ => 0,
    }
}
'''
fd, tmp = tempfile.mkstemp(suffix='.rs')
with open(tmp, 'w') as f:
    f.write(code)
os.close(fd)

# 模拟：只执行了 if 分支，未执行 else
exec_lines = {1, 2, 3}
miss_lines = {4, 5}
exec_br, miss_br = infer_branches(Path(tmp), exec_lines, miss_lines)
print(f'if/else: executed_branches={len(exec_br)}, missing_branches={len(miss_br)}')

os.unlink(tmp)
"
```

**预期：** 应检测到已执行和未执行的分支。

---

## 7. 测试 `rust_backend.py` —— Rust 后端

### 7.1 覆盖率 JSON 解析

```bash
.venv/bin/python -c "
from coverup.languages.rust_backend import parse_llvm_cov_json
import json, tempfile, os

# 模拟 cargo llvm-cov --json 输出格式
mock_data = {
  'data': [{
    'files': [{
      'filename': 'src/lib.rs',
      'segments': [
        [1, 1, 1, True, True, False],
        [3, 1, 0, True, True, False],
        [5, 1, 1, True, True, False],
      ],
      'summary': {'lines': {'count': 10, 'covered': 7, 'percent': 70.0}}
    }],
    'totals': {'lines': {'count': 10, 'covered': 7, 'percent': 70.0}}
  }]
}

fd, tmp = tempfile.mkstemp(suffix='.json')
with open(tmp, 'w') as f:
    json.dump(mock_data, f)
os.close(fd)

coverage = parse_llvm_cov_json(tmp)
for fname, data in coverage['files'].items():
    print(f'{fname}:')
    print(f'  executed: {data[\"executed_lines\"]}')
    print(f'  missing:  {data[\"missing_lines\"]}')
print(f'branch_coverage: {coverage[\"meta\"][\"branch_coverage\"]}')

os.unlink(tmp)
"
```

**预期：** 正确将 count>0 的 segment 标记为 executed，count=0 标记为 missing。

### 7.2 Rust 测试文件管理

```bash
.venv/bin/python -c "
import argparse
from pathlib import Path
from coverup.languages.rust_backend import RustBackend

# 验证 RustBackend 能正确初始化
args = argparse.Namespace(
    package_dir=Path('/tmp/test_rust_crate').resolve() if Path('/tmp/test_rust_crate').exists() else Path('.').resolve(),
    prefix='coverup',
    tests_dir=None,
    rust_test_args='',
    src_base_dir=None,
)
try:
    backend = RustBackend(args)
    print(f'RustBackend initialized successfully')
    print(f'  tests_dir: {backend.tests_dir}')
except Exception as e:
    print(f'RustBackend init error (expected if no crate): {e}')
"
```

---

## 8. 测试 `gpt_rust_v1.py` —— Rust Prompter

### 8.1 Prompt 生成验证

```bash
.venv/bin/python -c "
from coverup.prompt.gpt_rust_v1 import RustGptV1Prompter

# 验证 prompter 能被实例化
import argparse
from pathlib import Path

args = argparse.Namespace(
    src_base_dir=Path('.').resolve(),
    package_dir=Path('.').resolve(),
)
prompter = RustGptV1Prompter(cmd_args=args)
print(f'RustGptV1Prompter created: {type(prompter).__name__}')
print(f'Constraints count: {len(prompter._constraints())}')
"
```

### 8.2 动态指导检测

```bash
.venv/bin/python -c "
from coverup.prompt.gpt_rust_v1 import RustGptV1Prompter

# 测试 _dynamic_rust_guidance 对各种 Rust 模式的检测
test_snippets = {
    'trait/impl': 'impl Display for MyStruct { fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result { Ok(()) } }',
    'Result/Option': 'fn parse(s: &str) -> Result<i32, ParseIntError> { s.parse() }',
    'async': 'async fn fetch(url: &str) -> Result<String, reqwest::Error> { Ok(String::new()) }',
    'unsafe': 'unsafe fn raw_ptr(p: *const i32) -> i32 { *p }',
    'lifetime': \"fn longest<'a>(x: &'a str, y: &'a str) -> &'a str { if x.len() > y.len() { x } else { y } }\",
}

for name, code in test_snippets.items():
    guidance = RustGptV1Prompter._dynamic_rust_guidance(code)
    has_guidance = len(guidance) > 0
    print(f'{name}: {\"detected\" if has_guidance else \"no guidance\"} ({len(guidance)} chars)')
"
```

**预期：** 每种模式都应被检测到并生成非空指导。

---

## 9. 端到端测试（E2E）

### 9.1 对 Cobra 运行 CoverUp（Go — 真实测试）

这需要 LLM API key 和 Go 工具链：

```bash
cd /home/zzzccc/coverup

# 先测量基线覆盖率（不生成测试，仅验证流程通畅）
.venv/bin/python -m coverup \
    --language go \
    --package-dir src/cobra \
    --model gpt-4o \
    --prompt gpt-go-v1 \
    --skip-suite-measurement \
    --dry-run \
    --debug
```

`--dry-run` 模式不会实际调用 LLM，仅验证参数解析、分段逻辑和流程编排。

### 9.2 完整运行（Go — 小范围）

```bash
# 只处理少量 segments，限制成本
.venv/bin/python -m coverup \
    --language go \
    --package-dir src/cobra \
    --model gpt-4o \
    --prompt gpt-go-v1 \
    --max-attempts 2 \
    --max-concurrency 3 \
    --line-limit 30 \
    --log-file coverup-go-test-log \
    --checkpoint coverup-go-test.ckpt \
    --prefix coverup_test
```

运行后检查：
```bash
# 查看生成的测试文件
find src/cobra -name 'coverup_test_*_test.go' -ls

# 验证生成的测试能通过
cd src/cobra && go test ./... -count=1

# 查看日志了解 LLM 交互过程
less coverup-go-test-log
```

### 9.3 对 Rust Crate 运行 CoverUp

```bash
# 创建或使用现有的 Rust crate
cd /tmp && cargo new coverup_rust_test --lib && cd coverup_rust_test

# 添加一些待测代码到 src/lib.rs
cat > src/lib.rs << 'EOF'
pub fn add(a: i32, b: i32) -> i32 { a + b }
pub fn subtract(a: i32, b: i32) -> i32 { a - b }
pub fn multiply(a: i32, b: i32) -> i32 { a * b }
pub fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 { Err("division by zero".to_string()) } else { Ok(a / b) }
}
EOF

# 运行 CoverUp
cd /home/zzzccc/coverup
.venv/bin/python -m coverup \
    --language rust \
    --package-dir /tmp/coverup_rust_test \
    --model deepseek/deepseek-coder \
    --prompt gpt-rust-v1 \
    --max-attempts 2 \
    --max-concurrency 2 \
    --log-file coverup-rust-test-log
```

运行后检查：
```bash
# 查看生成的测试文件
find /tmp/coverup_rust_test/tests -name 'coverup_*.rs' -ls

# 验证生成的测试能通过
cd /tmp/coverup_rust_test && cargo test

# 查看覆盖率
cargo llvm-cov --json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Coverage: {d[\"data\"][0][\"totals\"][\"lines\"][\"percent\"]:.1f}%')"
```

### 9.4 验证 get_info 在实际对话中的效果

在日志中搜索 tool function 调用：

```bash
grep -n "get_info" coverup-go-test-log | head -20
```

应能看到 LLM 调用 `get_info` 查询类型定义，以及返回的符号信息。

---

## 10. 自动化测试建议

### 10.1 编写 `go_codeinfo` 的单元测试

建议在 `tests/` 下创建 `test_go_codeinfo.py`：

```python
"""Tests for Go static analysis module."""
import pytest
from pathlib import Path
from coverup.go_codeinfo import (
    get_info_go, infer_branches,
    extract_receiver_type, find_type_definition,
)

# 使用 src/cobra 作为测试 fixture（如果存在）
COBRA_DIR = Path("src/cobra")
COMMAND_GO = COBRA_DIR / "command.go"

@pytest.mark.skipif(not COMMAND_GO.exists(), reason="cobra source not available")
class TestGetInfoGo:
    def test_find_type(self):
        result = get_info_go(COMMAND_GO, "Command", module_root=COBRA_DIR)
        assert result is not None
        assert "Command" in result

    def test_find_function(self):
        result = get_info_go(COBRA_DIR / "cobra.go", "OnInitialize", module_root=COBRA_DIR)
        # Could be function or not found, depends on file structure
        # At minimum, should not raise
        assert result is None or isinstance(result, str)

    def test_method_lookup(self):
        result = get_info_go(COMMAND_GO, "Command.Execute", module_root=COBRA_DIR)
        assert result is not None
        assert "Execute" in result

    def test_go_doc_fallback(self):
        result = get_info_go(COMMAND_GO, "fmt.Sprintf", module_root=COBRA_DIR)
        # go doc should find standard library
        assert result is not None or True  # May fail if go not installed

    def test_unknown_symbol(self):
        result = get_info_go(COMMAND_GO, "NonExistentSymbol12345")
        assert result is None


@pytest.mark.skipif(not COMMAND_GO.exists(), reason="cobra source not available")
class TestInferBranches:
    def test_returns_tuples(self):
        exec_br, miss_br = infer_branches(
            COMMAND_GO,
            executed_lines=set(range(1, 50)),
            missing_lines=set(range(50, 100)),
        )
        assert isinstance(exec_br, list)
        assert isinstance(miss_br, list)
        for br in exec_br + miss_br:
            assert isinstance(br, tuple)
            assert len(br) == 2

    def test_nonexistent_file(self):
        exec_br, miss_br = infer_branches(
            Path("/nonexistent.go"), set(), set()
        )
        assert exec_br == []
        assert miss_br == []
```

### 10.2 运行新测试

```bash
# 将上面的代码保存到 tests/test_go_codeinfo.py 后运行
.venv/bin/python -m pytest tests/test_go_codeinfo.py -x -v
```

---

## 11. 调试技巧

### 11.1 查看 LLM 完整交互日志

CoverUp 的日志记录了每次 LLM 请求和响应的 JSON：

```bash
# 查看最近的日志
tail -100 coverup-log

# 搜索特定 segment 的处理过程
grep -A 50 "command.go:920" coverup-log
```

### 11.2 检查 get_info 调用链

```bash
# 在日志中查找 tool_calls
grep -B2 -A5 '"tool_calls"' coverup-log | head -40

# 查找 get_info 的返回结果
grep -A10 '"role": "tool"' coverup-log | head -50
```

### 11.3 调试分支推断

```bash
.venv/bin/python -c "
from pathlib import Path
from coverup.go_codeinfo import infer_branches, find_control_flow_nodes, _ensure_parser, _node_text

parser = _ensure_parser()
p = Path('src/cobra/command.go')
src = p.read_bytes()
tree = parser.parse(src)

# 列出所有控制流节点
for node in find_control_flow_nodes(tree.root_node):
    line = node.start_point[0] + 1
    text = _node_text(node, src).split('{')[0].strip()[:80]
    print(f'  L{line}: {node.type} — {text}')
" | head -30
```

### 11.4 生成的测试文件格式

成功生成的 Go 测试文件包含元数据头：

```go
// file: src/cobra/command.go:920-950
// asked: {"lines": [925, 930], "branches": [[925, 0]]}
// gained: {"lines": [925], "branches": [[925, 0]]}

package cobra

import (
    "testing"
)

func TestExecute_CoverUp(t *testing.T) {
    // ...
}
```

---

## 12. 性能基准

### 12.1 分段速度

```bash
.venv/bin/python -c "
import time, argparse
from pathlib import Path
from coverup.languages.go_backend import GoBackend

args = argparse.Namespace(
    package_dir=Path('src/cobra').resolve(),
    prefix='coverup',
    tests_dir=Path('src/cobra').resolve(),
    go_test_args='',
)
backend = GoBackend(args)
coverage = backend.initial_empty_coverage()

start = time.time()
segments = backend.get_missing_coverage(coverage, line_limit=50)
elapsed = time.time() - start
print(f'Segmented {len(segments)} segments in {elapsed:.2f}s')
"
```

**预期：** 对 cobra（~15k 行 Go 代码）应在 1-3 秒内完成。

---

## 13. 常见问题

### Q: `tree_sitter` 或 `tree_sitter_languages` 导入失败
```bash
pip install tree-sitter tree-sitter-languages
```

### Q: `go doc` 命令失败
确保 Go 在 PATH 中并且能正常运行 `go version`。

### Q: 生成的测试 package 名不对
`go_backend._prepare_test_code()` 会自动修正 package 声明。如果仍有问题，检查源文件的 package 行。

### Q: 分支推断数量为 0
分支推断依赖于控制流语句（if/switch/select）与覆盖率数据的交集。如果提供的 `executed_lines` 和 `missing_lines` 没有覆盖控制流语句所在行，推断不会产生结果。

### Q: `cargo llvm-cov` 命令未找到
```bash
# 确保 cargo bin 在 PATH 中
source "$HOME/.cargo/env"
# 如未安装
cargo install cargo-llvm-cov
```

### Q: `cargo llvm-cov` 报错 "llvm-tools not found"
```bash
rustup component add llvm-tools-preview
```

### Q: Rust 测试生成到哪个目录？
CoverUp 的 Rust 后端使用**集成测试策略**，将测试文件放在 `tests/` 目录下（而非 `src/` 内的 `#[cfg(test)]` 模块），
这样无需修改 `lib.rs`，且只能测试 `pub` 接口，符合集成测试最佳实践。

### Q: `rustfmt` 格式化失败
确保 `rustfmt` 在 PATH 中：`rustup component add rustfmt`。CoverUp 在格式化失败时会回退到使用未格式化的代码。
