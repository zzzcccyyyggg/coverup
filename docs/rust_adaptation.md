# Rust 语言适配文档

本文档记录 CoverUp 对 Rust 语言支持的完整实现过程，包括环境配置、新增模块、设计决策和验证结果。

---

## 1. 环境要求

### 1.1 Rust 工具链

| 工具 | 最低版本 | 用途 |
|------|---------|------|
| `rustc` | 1.70+ | Rust 编译器 |
| `cargo` | 1.70+ | 构建系统 & 包管理器 |
| `rustfmt` | 随 rustup 安装 | 代码格式化 |
| `cargo-llvm-cov` | 0.6+ | 覆盖率采集（基于 LLVM source-based coverage） |
| `llvm-tools-preview` | rustup 组件 | LLVM 覆盖率工具（`cargo-llvm-cov` 依赖） |

### 1.2 安装步骤

```bash
# 1. 安装 rustup（如未安装）
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# 2. 安装覆盖率组件
rustup component add llvm-tools-preview

# 3. 安装 cargo-llvm-cov
cargo install cargo-llvm-cov

# 4. 验证
rustc --version          # rustc 1.93.1 (01f6ddf75 2026-02-11)
cargo --version          # cargo 1.93.1 (083ac5135 2025-12-15)
rustfmt --version        # rustfmt 1.8.0-stable
cargo llvm-cov --version # cargo-llvm-cov 0.8.4
```

### 1.3 Python 依赖

```bash
pip install tree-sitter tree-sitter-languages
```

tree-sitter-languages 包含 Rust 语法解析器，无需额外编译。

---

## 2. 新增模块

### 2.1 `rust_codeinfo.py` — Rust 静态分析引擎（~470 行）

**路径：** `src/coverup/rust_codeinfo.py`

对标 Python 的 `codeinfo.py` 和 Go 的 `go_codeinfo.py`，为 Rust 提供静态分析能力：

| 函数 | 功能 |
|------|------|
| `get_info_rust(file, name)` | 符号查询：支持 `fn_name`、`TypeName`、`TypeName::method` 格式 |
| `infer_branches(path, executed, missing)` | 分析 `if`/`if let`/`match` 推断分支覆盖 |
| `extract_impl_type(node, source)` | 从 `impl` 块中提取目标类型名 |
| `find_type_definition(root, source, name)` | 查找 struct/enum/trait 的定义源码 |
| `_collect_methods_for_type(dir, type_name)` | 收集某类型在同目录中的所有方法签名 |

**符号查找策略：**
1. 优先在当前文件用 tree-sitter 搜索（fn/struct/enum/trait/impl/const/static/mod）
2. 对 `Type::method` 格式，定位 `impl Type` 块中的方法
3. 搜索同目录其他 `.rs` 文件
4. Fallback 到内置标准库文档（`_COMMON_STD` 字典，覆盖 40+ 常用类型）

**标准库文档覆盖范围：**
- 基础类型：`String`, `Vec`, `HashMap`, `HashSet`, `BTreeMap`, `BTreeSet`
- Option/Result 系列：`Option`, `Result`
- I/O：`File`, `BufReader`, `BufWriter`, `Read`, `Write`, `Path`, `PathBuf`
- 并发：`Arc`, `Mutex`, `RwLock`, `Condvar`, `mpsc`
- 迭代器：`Iterator`, `IntoIterator`
- 格式化：`Display`, `Debug`, `fmt::Formatter`
- 其他：`Box`, `Rc`, `Cell`, `RefCell`, `Cow`, `Pin`, `Duration`, `Instant`, `Regex`, `serde`

### 2.2 `rust_backend.py` — Rust 后端（~1650 行）

**路径：** `src/coverup/languages/rust_backend.py`

实现 `LanguageBackend` 接口，通过 `cargo llvm-cov` 采集覆盖率：

| 组件 | 功能 |
|------|------|
| `RustBackend` 类 | 后端主类，管理覆盖率测量、测试验证、代码分段 |
| `parse_llvm_cov_json()` | 解析 `cargo llvm-cov --json` 的 LLVM export 格式 |
| `_parse_segments_to_lines()` | 将 LLVM coverage segments 转换为行级执行/缺失集合 |
| `_register_temp_module()` | 集成测试策略 — 将测试放入 `tests/` 目录 |
| `_find_enclosing_node()` | tree-sitter AST 分段：fn/impl/struct/enum/trait/const/static/type/mod |
| `_resolve_crate_root()` | 从 `--source-dir` 向上查找 `Cargo.toml` 以确定 crate 根目录（V5） |
| `_build_api_map()` | 遍历 pub API 构建 item→module 映射（V6） |
| `_build_item_module_lookup()` | 从 API map 构建唯一/歧义 item 查找表（V6） |
| `_autofix_submodule_imports()` | 6 步自动修复子模块导入问题（V6） |
| `_generate_import_hints()` | 从编译错误中提取 "cannot find" 信息并生成导入建议（V6） |

**核心设计决策：**

1. **集成测试策略**：生成的测试放在 `tests/` 目录而非 `src/` 中的 `#[cfg(test)]` 模块
   - 优点：无需修改 `lib.rs`，不影响现有代码
   - 优点：使用 `use <crate_name>::*` 导入，只测试 pub 接口
   - 缺点：无法测试 private 函数

2. **单 crate 锁**：使用 `asyncio.Lock` 而非 Go 的 per-package 锁
   - Cargo 不支持同 crate 的并发编译
   - 所有 `cargo test` 调用串行执行

3. **覆盖率解析**：LLVM coverage segment 格式为 `[line, col, count, hasCount, isRegionEntry, isGap]`
   - `count > 0` 且 `isRegionEntry=True` → 已执行
   - `count == 0` 且 `isRegionEntry=True` → 未执行
   - Gap segments 被忽略

4. **错误输出清洗**：保留编译错误、panic、测试失败、断言信息，限制 40 行

5. **初始化检查**：`_check_llvm_cov()` 在构造时验证 `cargo-llvm-cov` 和 `llvm-tools-preview` 可用性

### 2.3 `gpt_rust_v1.py` — Rust Prompt 模板（~430 行）

**路径：** `src/coverup/prompt/gpt_rust_v1.py`

对标 Go 的 `gpt_go_v1.py`，为 Rust 提供 LLM 提示模板：

**17 条 Rust 专属约束：**
1. 每个测试函数必须标注 `#[test]`
2. 使用 `use <crate>::*` 导入
3. 不使用 `unsafe` 块（除非被测代码本身是 unsafe）
4. 使用 `assert!`、`assert_eq!`、`assert_ne!` 断言
5. 预期 panic 使用 `#[should_panic]` 而非 `catch_unwind`
6. 不依赖外部 crate
7. 使用 `tempfile` 或 `std::env::temp_dir()` 处理文件系统
8. 错误处理使用 `.unwrap()` 或 `?`（测试中）
9. 泛型函数用具体类型实例化
10. async 函数使用 `#[tokio::test]` 或手动 `block_on`
11. 不修改全局状态
12. 保持测试独立（不依赖执行顺序）
13. 使用描述性测试名（snake_case）
14. lifetime 参数正确标注
15. 不假设 struct 字段可直接访问（可能为 private）
16. 实现 trait 测试时创建 test struct
17. 使用 `Vec`/`String` 而非 `&[T]`/`&str` 作为 owned 数据

**动态代码分析（`_dynamic_rust_guidance()`）检测：**
- trait/impl 模式 → 建议创建 mock struct
- Result/Option → 建议测试 Ok/Err、Some/None 路径
- async 代码 → 建议使用 `tokio::test`
- lifetime 注解 → 提醒正确处理借用
- unsafe 代码 → 提醒最小化 unsafe 范围
- 泛型参数 → 建议用具体类型测试
- 文件系统操作 → 建议使用临时目录
- 网络/HTTP → 建议创建 mock 或绑定 localhost
- Mutex/RwLock → 提醒并发场景
- serde → 建议测试序列化/反序列化往返
- match 表达式 → 建议覆盖所有分支
- 闭包/高阶函数 → 建议测试不同闭包参数

---

## 3. `coverup.py` 注册改动

在主 CLI 模块 `src/coverup/coverup.py` 中添加 Rust 支持的注册代码：

```python
# 导入
from .languages.rust_backend import RustBackend

# Prompter 注册（在 get_prompters() 中）
"gpt-rust-v1": RustGptV1Prompter

# CLI 参数
choices=['python', 'go', 'rust']

# 语言特定参数处理
elif args.language == 'rust':
    args.src_base_dir = args.package_dir / "src"
    args.tests_dir = args.package_dir / "tests"
    args.branch_coverage = True
    if not args.prompt:
        args.prompt = "gpt-rust-v1"

# 后端映射
'rust': RustBackend
```

---

## 4. 覆盖率数据流

### 4.1 `cargo llvm-cov` 输出格式

```json
{
  "data": [{
    "files": [{
      "filename": "src/lib.rs",
      "segments": [
        [1, 1, 5, true, true, false],
        // [line, col, count, hasCount, isRegionEntry, isGap]
      ],
      "summary": {
        "lines": {"count": 100, "covered": 70, "percent": 70.0}
      }
    }],
    "totals": {
      "lines": {"count": 100, "covered": 70, "percent": 70.0}
    }
  }]
}
```

### 4.2 CoverUp 内部覆盖率格式

`parse_llvm_cov_json()` 将 LLVM 格式转换为 CoverUp 统一格式：

```json
{
  "files": {
    "src/lib.rs": {
      "executed_lines": [1, 2, 5, 7],
      "missing_lines": [3, 4, 6],
      "executed_branches": [[2, 3]],
      "missing_branches": [[5, 0]]
    }
  },
  "meta": {
    "branch_coverage": true
  },
  "summary": {
    "percent_covered": 70.0
  }
}
```

### 4.3 Segment → Line 转换算法

LLVM coverage segments 描述区域的起始位置和执行计数。`_parse_segments_to_lines()` 将其转换为行级数据：

1. 按 `(line, col)` 排序 segments
2. 遍历 segments：
   - `isGap=True` → 跳过
   - `isRegionEntry=True` → 开始新区域
   - 后续行继承当前区域的 `count` 直到下一个 segment
3. `count > 0` → `executed_lines`
4. `count == 0` → `missing_lines`

---

## 5. 验证结果

### 5.1 导入验证

```
$ .venv/bin/python -c "from coverup.rust_codeinfo import get_info_rust, infer_branches; ..."
All Rust imports OK
```

### 5.2 tree-sitter Rust 解析器

```
$ .venv/bin/python -c "from tree_sitter_languages import get_parser; p=get_parser('rust'); ..."
Rust parser: <tree_sitter.Language ...>
```

### 5.3 rust_codeinfo 功能测试

| 测试 | 输入 | 结果 |
|------|------|------|
| `get_info_rust(f, "add")` | 函数名 | ✅ 返回函数定义 |
| `get_info_rust(f, "Calculator")` | struct 名 | ✅ 返回 struct + impl 方法列表 |
| `get_info_rust(f, "Calculator::new")` | impl 方法 | ✅ 返回方法定义 |
| `get_info_rust(f, "Color")` | enum 名 | ✅ 返回 enum 定义 |
| `get_info_rust(f, "Drawable")` | trait 名 | ✅ 返回 trait 定义 |
| `infer_branches(f, exec, miss)` | 控制流代码 | ✅ 正确推断分支 |

### 5.4 覆盖率解析验证

使用真实的 `cargo llvm-cov --json` 输出（`/tmp/test_rust_crate`）：

```
parse_llvm_cov_json 结果:
  executed_lines:  [1, 2, 3, 7, 32, 33, 34]  (7 行)
  missing_lines:   [5, 14, 15, 16, 17, 18, 19, 20, 21, 24]  (10 行)
  executed_branches: [(2, 3)]  (1 个)
  missing_branches: []
  总覆盖率: 41.18%
```

与 `cargo llvm-cov` 报告的 41.18% 一致。

### 5.5 CLI 确认

```
$ .venv/bin/python -m coverup --help | grep -A1 "language"
  --language {python,go,rust}
```

### 5.6 现有测试无回归

```
$ .venv/bin/python -m pytest tests/test_codeinfo.py -x -q
32 passed, 1 skipped
```

---

## 6. 使用示例

### 6.1 基本用法

```bash
# 对 Rust crate 运行 CoverUp
.venv/bin/python -m coverup \
    --language rust \
    --package-dir /path/to/my_crate \
    --model deepseek/deepseek-coder \
    --prompt gpt-rust-v1
```

### 6.2 控制并发和重试

```bash
.venv/bin/python -m coverup \
    --language rust \
    --package-dir /path/to/my_crate \
    --model deepseek/deepseek-coder \
    --prompt gpt-rust-v1 \
    --max-attempts 3 \
    --max-concurrency 2 \
    --line-limit 40 \
    --log-file coverup-rust-log \
    --checkpoint coverup-rust.ckpt
```

### 6.3 查看覆盖率变化

```bash
# 运行前基线
cd /path/to/my_crate
cargo llvm-cov --json | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'基线覆盖率: {d[\"data\"][0][\"totals\"][\"lines\"][\"percent\"]:.1f}%')
"

# 运行 CoverUp 后
cargo llvm-cov --json | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'最终覆盖率: {d[\"data\"][0][\"totals\"][\"lines\"][\"percent\"]:.1f}%')
"
```

---

## 7. 与 Go 适配的对比

| 方面 | Go | Rust |
|------|-----|------|
| 覆盖率工具 | `go test -coverprofile`（文本格式） | `cargo llvm-cov --json`（LLVM JSON 格式） |
| 覆盖率精度 | 行+语句范围 | 行+region 级别（更精确） |
| 测试位置 | 同包 `_test.go` | `tests/` 目录（集成测试） |
| 符号查找 fallback | `go doc` 命令 | 内置标准库文档字典 |
| 并发控制 | per-package 锁 | 单 crate 全局锁 |
| 格式化工具 | `goimports`（需发现路径） | `rustfmt`（随 rustup 安装） |
| 分支推断 | if/switch/select | if/if_let/match |
| 依赖管理 | `go mod tidy` 自动重试 | cargo 内置依赖解析 |
| 动态指导 | 8 种模式 | 12 种模式 |
| Prompt 约束 | 3 条额外 | 17 条约束 |

---

## 8. 已知限制

1. **仅测试 pub 接口**：集成测试无法访问 private 函数/字段
2. **单 crate 锁**：并发度受限，大项目可能较慢
3. **无 workspace 支持**：当前只处理单个 crate，不支持 Cargo workspace 多 crate
4. **标准库文档非完整**：内置文档覆盖 40+ 常用类型，不支持第三方 crate 文档查询
5. **分支推断有限**：仅处理 if/if_let/match，不处理 `?` 操作符的分支
6. **async 测试需要 tokio**：如目标 crate 未依赖 tokio，async 测试可能需要手动添加依赖

---

## 9. 后续改进方向

- [ ] 支持 `cargo-nextest` 作为替代测试运行器
- [ ] 支持 Cargo workspace 多 crate 并行测试
- [ ] 添加 `rustdoc` 查询作为标准库文档 fallback
- [ ] 支持 `#[cfg(test)]` 内联测试模式（可测 private 函数）
- [ ] 增加 `?` 操作符的分支推断
- [ ] 支持 proc-macro crate 的特殊处理

---

## 10. V5 改进：Crate 根目录解析修复

### 10.1 问题背景

V3 版本在 `similar` crate 上表现极差（G=1, F=7, U=296），而 V2 期望值为 G=30, F=148, U=155。

### 10.2 根因分析

发现三个级联 Bug：

1. **`--source-dir` 导致 `crate_root` 错误**：用户传入 `--source-dir /tmp/similar/src`，后端将 `src/` 作为 crate root，导致 `Cargo.toml` 找不到
2. **`_detect_crate_name()` 失败**：因为在 `src/` 下找不到 `Cargo.toml`，crate 名回退为 `"crate"`
3. **生成测试使用 `use crate::*`**：集成测试文件中 `use crate::*` 无法编译（只在 `#[cfg(test)]` 内联测试中合法）

### 10.3 V5 修复方案

```python
@staticmethod
def _resolve_crate_root(source_dir: Path) -> Path:
    """从 source_dir 向上查找 Cargo.toml 确定 crate 根目录"""
    d = source_dir.resolve()
    while d != d.parent:
        if (d / "Cargo.toml").exists():
            return d
        d = d.parent
    return source_dir  # fallback
```

同时修复了 `_crate_name` 属性和 `use crate::` → `use <crate_name>::` 的替换逻辑。

### 10.4 V5 结果

在 `similar` crate 上：**G=45, F=243, U=13, 覆盖率 93.9%**（从 G=1 提升到 G=45）

---

## 11. V6 改进：自动修复子模块导入

### 11.1 问题背景

V5 虽然大幅提升了成功率，但 F=243 的失败数仍然很高。分析发现主要错误类型：

| 错误码 | 含义 | V5 出现次数 |
|--------|------|------------|
| E0425 | cannot find value/function | 2149 |
| E0433 | failed to resolve module path | 1520 |
| E0061 | wrong number of arguments | 1017 |
| E0599 | no method found for type | 930 |
| E0659 | ambiguous glob re-export | 392 |
| E0451 | field is private | 677 |

根因：LLM 只生成 `use similar::*`，但很多 item 在子模块中（如 `similar::algorithms::diff_slices`），需要显式导入子模块。此外 `use similar::*` 加上 `use similar::algorithms::*` 会导致 E0659 歧义错误。

### 11.2 V6 三项改进

#### 11.2.1 `_autofix_submodule_imports()` — 自动修复导入

6 步自动修复流程：

1. **收集现有 import**：解析测试代码中已有的 `use` 语句
2. **检测需要子模块导入的 item**：从编译错误中识别 "cannot find" 的函数/类型
3. **查找 item 所属模块**：通过 API map 查询 item→module 映射
4. **修复错误的限定路径**：如 `crate::module::item` → `<crate_name>::module::item`
5. **添加缺失的 glob import**：自动追加 `use <crate>::<submodule>::*;`
6. **解决 E0659 歧义**：当根 glob 与子模块 glob 冲突时，将子模块 glob 改为精确导入

#### 11.2.2 增强 `format_test_error()` — 错误格式化

- **噪音过滤**：移除 `aborting due to`, `warning:`, `Compiling`, `For more information` 等无用信息
- **去重**：相同错误描述只保留首次出现
- **行数限制**：最多 40 行，避免超出 LLM 上下文
- **导入建议**：调用 `_generate_import_hints()` 在错误末尾追加使用建议

#### 11.2.3 增强 Prompt 约束

在 `gpt_rust_v1.py` 的 `_constraints()` 中新增两条约束：

```
- Items not found at the crate root must be imported from their specific
  submodule (e.g., `use {crate}::algorithms::*;`).
- Avoid importing the same item via multiple glob imports to prevent E0659
  ambiguity errors. Prefer targeted imports over broad glob imports.
```

### 11.3 V6 效果对比（`similar` crate）

| 错误码 | V5 | V6 | 变化 |
|--------|-----|-----|------|
| E0659 (歧义) | 392 | **0** | **-100%** ✅ |
| E0425 (找不到值) | 2149 | 263 | **-88%** ✅ |
| E0433 (路径解析) | 1520 | 271 | **-82%** ✅ |
| E0451 (私有字段) | 677 | 72 | **-89%** ✅ |
| E0599 (方法未找到) | 930 | 2244 | +141% ⚠️ |

> **注意**：E0599 增加是因为导入修复后，更多测试通过了编译的导入阶段，暴露了更深层的 API 误用错误。这是预期行为。

---

## 12. 多项目基准测试结果

使用 V6 版本在三个不同 Rust crate 上进行测试，LLM 为 DeepSeek Coder，参数 `--max-attempts 5 --max-concurrency 5`：

### 12.1 总体结果

| 项目 | 版本 | 源码行数 | 源文件数 | Segments | Good | Failed | Useless | 初始覆盖率 | 最终覆盖率 | 费用 | 耗时 |
|------|------|---------|---------|----------|------|--------|---------|-----------|-----------|------|------|
| **similar** | v2.7.0 | ~3500 | 多文件 | 41 | 43 | 226 | 17 | ~70% | **93.1%** | ~$0.35 | ~8min |
| **semver** | v1.0.27 | 2117 | 7 | 22 | 18 | 21 | 9 | 91.7% | **98.8%** | ~$0.07 | ~6min |
| **strsim-rs** | v0.11.1 | 1303 | 1 | 10 | 8 | 6 | 3 | 85.4% | **97.0%** | ~$0.05 | ~3min |

### 12.2 成功率分析

| 项目 | Good 率 | 说明 |
|------|---------|------|
| **strsim-rs** | 47% (8/17) | API 简洁，函数签名清晰，LLM 容易正确调用 |
| **semver** | 38% (18/48) | API 较规范，但部分 segment 涉及复杂解析逻辑 |
| **similar** | 15% (43/286) | 子模块结构复杂，同名 item 多处导出导致歧义 |

### 12.3 项目特征差异

| 特征 | similar | semver | strsim-rs |
|------|---------|--------|-----------|
| API 结构 | 多子模块，重新导出，歧义 | 扁平结构，std traits 丰富 | 单文件，纯函数 |
| 主要错误 | E0425, E0599 (#[kw]API 误用) | E0277, E0433, E0015 (类型约束) | E0425 (部分函数名) |
| 错误分布 | 编译错误为主 (222/265) | 编译错误为主 | 编译错误为主 |
| 覆盖率提升 | +23.1pp | +7.1pp | +11.6pp |

### 12.4 各项目错误分布

**semver 主要错误：**

| 错误码 | 含义 | 次数 |
|--------|------|------|
| E0277 | trait bound not satisfied | 22 |
| E0433 | failed to resolve path | 19 |
| E0015 | cannot call non-const fn in const | 18 |
| E0599 | no method found | 8 |
| E0432 | unresolved import | 4 |

**strsim-rs 主要错误：**

| 错误码 | 含义 | 次数 |
|--------|------|------|
| E0425 | cannot find value/function | 30 |
| E0308 | mismatched types | 4 |

---

## 13. 后续改进方向

### 已完成
- [x] V5：修复 crate root 解析和 crate name 检测
- [x] V6：自动修复子模块导入（E0659 歧义完全消除，E0425/E0433 减少 80%+）
- [x] V6：增强错误格式化和导入建议
- [x] 多项目基准测试（similar, semver, strsim-rs）

### 待完成
- [ ] 减少 E0599（方法未找到）错误：在 prompt 中提供更精确的方法签名信息
- [ ] 减少 E0277（trait bound 不满足）错误：在代码上下文中包含相关 trait 实现
- [ ] 支持 `cargo-nextest` 作为替代测试运行器
- [ ] 支持 Cargo workspace 多 crate 并行测试
- [ ] 添加 `rustdoc` 查询作为标准库文档 fallback
- [ ] 支持 `#[cfg(test)]` 内联测试模式（可测 private 函数）
- [ ] 增加 `?` 操作符的分支推断
- [ ] 支持 proc-macro crate 的特殊处理
