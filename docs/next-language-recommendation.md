# 下一语言适配建议

## 当前状态

CoverUp 目前支持两种语言：

| 语言 | 后端 | 覆盖率工具 | 静态分析 | Prompt | 状态 |
|------|------|-----------|---------|--------|------|
| Python | `python_backend.py` | SlipCover | `codeinfo.py` (AST) | `gpt_v2.py` / `claude.py` | ✅ 成熟 |
| Go | `go_backend.py` | `go test -coverprofile` | `go_codeinfo.py` (tree-sitter) | `gpt_go_v1.py` | ✅ 可用（97.7% on cobra） |

---

## 推荐顺序

### 🥇 第一推荐：Rust

**推荐理由：架构契合度最高，Go 适配经验可直接复用**

#### 优势

1. **工具链高度统一**
   - `cargo test` 内置测试框架，无需选择（不像 JS 有 jest/vitest/mocha 分裂）
   - `cargo-llvm-cov` 提供源码级覆盖率，输出 JSON 格式，类似 Go 的 `coverprofile`
   - `cargo` 统一管理依赖、编译、测试，类似 Go 的 `go mod` + `go test`

2. **与 Go 后端的相似性**
   - 编译型语言 → 编译→运行→覆盖率 三步循环
   - 测试文件可以与源码同目录（`#[cfg(test)] mod tests`）或独立 `tests/` 目录
   - 依赖解析由 cargo 处理，类似 `go mod tidy`
   - tree-sitter-rust 解析器成熟稳定

3. **LLM 生成质量可控**
   - Rust 编译器错误信息极其详细且有修复建议 → 非常适合 error prompt 回馈
   - 类型系统严格 → LLM 犯错时编译器能拦截大部分问题
   - 标准 `assert!`、`assert_eq!`、`#[should_panic]` 模式固定，LLM 容易掌握

4. **市场价值**
   - Rust 生态快速增长（Linux kernel、Android、AWS、Cloudflare 等大规模采用）
   - 安全关键代码对测试覆盖率要求极高
   - 现有 Rust 覆盖率工具（tarpaulin、llvm-cov）功能强但无 AI 辅助

#### 实现难点

| 挑战 | 难度 | 应对策略 |
|------|------|---------|
| 生命周期/借用语义 | ⭐⭐⭐ | LLM 常犯借用错误，但 rustc 报错明确，可回馈修正 |
| 泛型与 trait bound | ⭐⭐ | prompt 中提供完整类型签名 + trait 定义 |
| unsafe 代码 | ⭐⭐ | 约束 LLM 不要生成 unsafe 测试代码 |
| 宏展开 | ⭐⭐ | `cargo expand` 可展开宏，必要时向 LLM 提供展开结果 |
| 编译时间 | ⭐⭐ | 增量编译缓解，但首次编译较慢 |

#### 需要实现的组件

```
src/coverup/languages/rust_backend.py    # ~800 行
src/coverup/rust_codeinfo.py             # ~400 行（tree-sitter-rust）
src/coverup/prompt/gpt_rust_v1.py        # ~300 行
```

#### 覆盖率工具集成

```bash
# 安装
cargo install cargo-llvm-cov

# 基线覆盖率（JSON 输出）
cargo llvm-cov --json --output-path coverage.json

# 单个测试覆盖率
cargo llvm-cov --json --output-path cov.json -- --test-threads=1 -t test_name

# 输出格式（llvm-cov export JSON）
{
  "data": [{
    "files": [{
      "filename": "src/lib.rs",
      "summary": { "lines": { "count": 100, "covered": 85 } },
      "segments": [[line, col, count, hasCount, isRegionEntry], ...]
    }]
  }]
}
```

#### 估计工作量

| 任务 | 预估时间 |
|------|---------|
| `rust_backend.py` 核心实现 | 3-4 天 |
| `rust_codeinfo.py` 静态分析 | 2-3 天 |
| `gpt_rust_v1.py` Prompt 设计 | 1-2 天 |
| 调试 + 真实项目验证 | 2-3 天 |
| **总计** | **8-12 天** |

---

### 🥈 第二推荐：TypeScript

**推荐理由：用户基数最大，LLM 生成质量最好**

#### 优势

1. **LLM 理解度极高** — 训练数据中 TS/JS 占比最大，生成质量最好
2. **快速迭代** — 无需编译（或 esbuild 极快编译），测试执行速度快
3. **用户基数** — 前端/后端/全栈开发者都是潜在用户
4. **覆盖率成熟** — v8 原生覆盖率 / c8 / istanbul 均支持 JSON 输出

#### 挑战

| 挑战 | 难度 | 说明 |
|------|------|------|
| 测试框架分裂 | ⭐⭐⭐ | jest / vitest / mocha / ava / tap — 需要检测或用户指定 |
| TS 配置多样 | ⭐⭐⭐ | tsconfig.json 变体多，paths / moduleResolution 差异大 |
| 模块系统混乱 | ⭐⭐⭐ | CJS vs ESM、import vs require、.mjs/.cjs 后缀 |
| mock 模式复杂 | ⭐⭐ | 需要理解 jest.mock / vi.mock / sinon 等 mock 注入方式 |

#### 需要实现的组件

```
src/coverup/languages/typescript_backend.py   # ~700 行
src/coverup/ts_codeinfo.py                    # ~350 行（tree-sitter-typescript）
src/coverup/prompt/gpt_ts_v1.py               # ~300 行
```

#### 估计工作量：10-15 天

---

### 🥉 第三推荐：Java

**推荐理由：企业市场需求大，工具链成熟**

#### 优势

1. **JaCoCo** 覆盖率工具极其成熟，支持行 + 分支 + 方法级覆盖
2. **JUnit 5** 几乎是唯一主流测试框架，没有 JS 的分裂问题
3. **LLM 对 Java 理解良好**，生成的测试代码通常结构正确

#### 挑战

| 挑战 | 难度 | 说明 |
|------|------|------|
| 构建系统复杂 | ⭐⭐⭐⭐ | Maven vs Gradle，各自配置差异巨大 |
| 包/类路径管理 | ⭐⭐⭐ | classpath 配置复杂，模块系统（Java 9+）增加复杂度 |
| 样板代码 | ⭐⭐ | Java 测试代码冗长，占 LLM token 多 |
| Spring 等框架 | ⭐⭐ | 企业代码通常依赖 DI 框架，测试需要特殊设置 |

#### 估计工作量：12-18 天

---

## 综合对比矩阵

| 维度 | Rust | TypeScript | Java |
|------|------|-----------|------|
| 工具链一致性 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| LLM 生成质量 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 与 Go 后端复用度 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| 用户基数/市场 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 覆盖率工具质量 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 实现难度（低=好） | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| 覆盖率提升价值 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## 最终建议

> **推荐先适配 Rust。** 原因：
> 1. 架构上与 Go 最接近（编译型、单一工具链、内置测试框架），Go 后端的实现模式可直接套用
> 2. `cargo-llvm-cov` 的 JSON 输出与现有覆盖率解析逻辑对齐
> 3. Rust 编译器的详细错误信息是天然的 error prompt 素材，比 Go 更丰富
> 4. Rust 代码的安全关键性意味着高覆盖率有极高实际价值
> 5. 现有 Rust 生态缺乏 AI 辅助覆盖率工具，差异化竞争优势明显

如果优先考虑**用户数量而非架构契合度**，则 TypeScript 是更好的选择。

---

## Rust 适配路径草案

### Step 1: Backend 骨架
```python
# src/coverup/languages/rust_backend.py
class RustBackend(LanguageBackend):
    def __init__(self, args):
        self.cargo_cmd = shutil.which("cargo") or "cargo"
        self._llvm_cov_installed = self._check_llvm_cov()
    
    def measure_suite_coverage(self, ...) -> dict:
        # cargo llvm-cov --json → 解析 llvm-cov export format
        
    async def measure_test_coverage(self, segment, test_code, ...) -> dict:
        # 写入临时 test module → cargo test → 解析覆盖率
        
    def get_missing_coverage(self, coverage, line_limit) -> list[CodeSegment]:
        # tree-sitter-rust 解析 → 定位未覆盖函数/impl块/match分支
```

### Step 2: 静态分析
```python
# src/coverup/rust_codeinfo.py
def get_info_rust(file, name, crate_root):
    # tree-sitter 查找 fn/struct/enum/trait/impl 定义
    # fallback: cargo doc --document-private-items

def infer_branches(path, executed, missing):
    # 分析 if/else, match/arm, ? operator, unwrap 等
```

### Step 3: Prompt 模板
```python
# src/coverup/prompt/gpt_rust_v1.py
class RustGptV1Prompter(Prompter):
    def _constraints(self):
        return [
            "Use #[test] functions in a #[cfg(test)] mod tests block",
            "Do NOT use unsafe unless the target code requires it",
            "Use assert!, assert_eq!, assert_ne! for assertions",
            "For error paths, use .unwrap_err() or matches!() macro",
            ...
        ]
```

### Step 4: 注册到 coverup.py
```python
# coverup.py
from .languages.rust_backend import RustBackend

# parse_args: choices=['python', 'go', 'rust']
# backend_map: {'rust': RustBackend}
```
