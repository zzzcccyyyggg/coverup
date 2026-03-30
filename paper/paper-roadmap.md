# CoverAgent-ML → CCF-B 论文改进路线图

> 基于 v3 (P0-P5 全部实现 + 跨语言实验完成) + 论文对比分析  
> 最后更新: 2026-02-17

---

## 0. 现状诊断：够不够？差什么？

### 0.1 我们有什么

| 维度 | 现状 | 论文可用性 |
|------|------|-----------|
| Recipe Memory (P1) | 468行, SuccessLevel 分层, UCB×recency 排序, 14 个预置处方 | ✅ 核心贡献 |
| UCB Planner (P2+P4) | 336行, select_batch 波次调度, plateau 检测, gap_complexity | ✅ 核心调度创新 |
| Tool-First Repair (P3) | 379行, 7 个内置 fixer, 两阶段修复 | ✅ 工程贡献 |
| Coverage Blocker (P5) | 727行, tree-sitter/ast 条件提取 + 变量来源追溯 | ✅ 方法学创新 |
| DiagnosticIR | 278行, 统一 13 类错误 × 6 阶段，frozen dataclass | ✅ 统一中间表示 |
| TraceLogger | 99行, 结构化 JSONL 追踪日志 | ✅ 可复现性基础 |
| 实验数据 | **4 个项目 (fastrand/Flask/cobra/similar)**, 跨 3 种语言 | ⚠️ 初步可用，规模需扩大 |
| 多语言验证 | **Rust ×2 + Python ×1 + Go ×1**, Agent vs Baseline A/B | ⚠️ 已有跨语言证据，但需更多项目 |
| 论文对比 | CoverUp/PALM/RUG 数据已提取，Flask 上胜过 CoverUp+GPT-4o | ✅ 有竞争力的故事 |

### 0.2 关键 gap (更新后)

```
[⚠️ 中等] 实证 4 个项目、每配置 1 次运行 → 需扩大到 10-15 个 + 重复实验
[✅ 已解决] P5 Coverage Blocker 已实现 → 方法学创新已有
[⚠️ 中等] Planner 收益未与"波次形态"隔离 → 需 wave-baseline 变体
[✅ 已解决] Memory SuccessLevel 已实现分层 → COMPILE/PARTIAL/FULL
[⚠️ 中等] Agent 在小项目上负收益 (fastrand -1.3pp, cobra -0.4pp) → 需自适应调节
[⚠️ 中等] Agent 过早终止 (1 pass vs baseline 2 pass) → 需最小 pass 控制
[⚠️ 低等] Blocker 隐式 else 未追踪 (TODO L282) → 小优化
```

### 0.3 竞争态势

| 工作 | 会议 | 核心贡献 | 我们的差异化点 |
|------|------|---------|--------------|
| **CoverUp** | FSE'25 | 迭代覆盖反馈 + LLM 对话 (Python-only) | 我们: 统一 IR + 在线决策 + 跨语言 |
| **RUG** | ICSE'25 | 语义感知自底向上上下文 + 覆盖导向 (Rust-only) | 我们: Recipe 学习 + 预算分配，不仅是单次上下文 |
| **PALM** | ASE'25 | 程序分析提取分支条件/路径约束 → 引导 LLM (Rust-only) | 我们: 轻量动态证据 + 跨语言条件解释 (P5) |
| **ASTER** | ICSE'25 | 多语言 (Java+Python) + 静态分析 + 可读性/用户研究 | 我们: **在线**决策闭环 + 预算约束下效率优化 |

**定位策略**：
- 主故事 = **Blocker**: "from missing lines to reachability conditions" — CoverUp/RUG 说 where，PALM 说 why (重量级)，我们说 **why + how (轻量级 + 跨语言)**
- 第二故事 = **Recipe Memory**: "不只是学成功率，而是分层学到修到能编译/能跑/能涨覆盖" — 首个将分层成功信号用于测试生成经验积累
- Planner 降格为系统贡献，不强调 bandit 算法新颖性，强调"让决策进入控制流 + 支持消融"

---

## 1. P5: Coverage Blocker Explanation — 核心方法创新

### 1.1 动机

当前 LLM 收到的信息是 **"line 42 does not execute"**（where）。LLM 缺少的是 **"为什么 line 42 没执行 + 需要什么条件才能到达"**（why + how）。这直接导致 Useless (U) 上升：LLM 能写出编译通过的测试，但构造的输入无法触发目标分支。

```
CoverUp  → "lines 42-48 do not execute"           (WHERE)
PALM     → 静态路径约束（完整路径可行性分析）        (WHY, 重量级, Rust-only)
P5(ours) → "line 42 needs `x > 0`; current tests   (WHY + HOW, 轻量, 跨语言)
            only reach x ≤ 0; x comes from 
            parameter `config.threshold`"
```

### 1.2 P5 形式化定义

**定义 (Coverage Blocker)**：给定目标未覆盖行 $\ell$，其最近的控制流支配条件为 $P(\ell)$。Coverage Blocker 是一个三元组：

$$B = \langle P(\ell),\ \text{source}(P),\ \text{hint}(P) \rangle$$

- $P(\ell)$: 控制条件的源码文本（如 `x > 0`、`matches!(val, Some(_))`）
- $\text{source}(P)$: 条件中变量的追溯来源（参数、返回值、字段）
- $\text{hint}(P)$: 到达建议（如 "construct input where `config.threshold > 0`"）

### 1.3 实现方案：三层提取

```
Layer 1: Predicate Extraction (tree-sitter, 纯静态)
  现有 find_control_flow_nodes() + 新增 extract_predicate_text()
  → 获取每个未覆盖分支的守护条件文本

Layer 2: Variable Origin Tracing (tree-sitter, 纯静态)  
  新增 trace_predicate_variables()
  → 追溯条件中每个变量的来源：参数/字段/返回值/局部计算

Layer 3: Reachability Hint Generation (模板 + 可选 LLM)
  新增 generate_blocker_hint()
  → 组合 Layer 1+2 生成结构化提示文本
```

### 1.4 代码改动清单

#### 1.4.1 新增模块: `src/coverup/agents/blocker.py`

```python
"""Coverage Blocker Explanation — P5 核心创新模块.

从"未覆盖行号"提升到"可执行的到达条件提示"，
显著减少 Useless (编译通过但不涨覆盖) 的比例。
"""

@dataclass(frozen=True)
class CoverageBlocker:
    """一个未覆盖分支的阻塞解释."""
    target_line: int              # 目标未覆盖行
    predicate_line: int           # 守护条件所在行
    predicate_text: str           # 条件表达式文本 (e.g. "x > 0")
    predicate_kind: str           # "if" | "match_arm" | "guard" | "while" | ...
    variables: List[VariableOrigin]  # 条件中变量的来源追溯
    hint: str                     # 生成的到达建议文本
    confidence: float             # 0-1, 基于追溯深度

@dataclass(frozen=True)
class VariableOrigin:
    """条件中单个变量的来源."""
    name: str                     # 变量名
    origin_kind: str              # "parameter" | "field" | "return_value" | "local" | "constant" | "unknown"
    origin_detail: str            # e.g. "parameter `config` of fn `process()`"
    type_hint: Optional[str]      # 类型信息 (如果 tree-sitter 能提取)


def extract_blockers(
    path: Path,
    missing_lines: Set[int],
    missing_branches: Set[Tuple[int, int]],
    executed_lines: Set[int],
    language: str,                # "rust" | "python" | "go"
    max_blockers: int = 5,
) -> List[CoverageBlocker]:
    """提取未覆盖分支的阻塞解释."""
    ...

def format_blockers_for_prompt(
    blockers: List[CoverageBlocker],
    max_chars: int = 800,
) -> str:
    """将 blocker 列表格式化为 LLM prompt 注入文本."""
    ...
```

#### 1.4.2 各语言 tree-sitter 提取器

在 `rust_codeinfo.py`, `go_codeinfo.py` 各新增一个函数：

```python
def extract_predicate_for_branch(
    path: Path,
    branch_from_line: int,
    branch_to_line: int,
) -> Optional[dict]:
    """提取分支守护条件的结构化信息.
    
    Returns:
        {
            "predicate_text": "x > 0",
            "predicate_kind": "if",
            "predicate_line": 42,
            "variables": ["x"],
            "variable_types": {"x": "i32"},  # best-effort
        }
    """
```

**实现思路**：  
- 已有 `find_control_flow_nodes()` 定位 if/match/switch 节点
- 新增：对每个节点提取 `condition` 子字段的文本（`node.child_by_field_name("condition")`）
- 对 match: 提取对应 arm 的 pattern 文本
- 变量追溯：在条件文本中用 tree-sitter 找 `identifier` 节点，然后在函数体内向上搜索其定义/赋值/参数列表

#### 1.4.3 Python 的处理

Python 使用 `ast` 模块而非 tree-sitter，但逻辑相同：

```python
# codeinfo.py 新增
def extract_predicate_for_branch_python(
    module: Module,
    branch_from_line: int,
    branch_to_line: int,
) -> Optional[dict]:
    """从 Python AST 提取分支条件."""
    # ast.If → node.test
    # ast.Match → node.cases[i].pattern  (Python 3.10+)
    # ast.While → node.test
```

Python 比 Rust/Go 更简单，因为 SlipCover 直接提供 `missing_branches` 且 AST 更易遍历。

#### 1.4.4 Prompt 注入点

在 `gpt_rust_v1.py` 的 `initial_prompt()` 和 `missing_coverage_prompt()` 中：

```python
# initial_prompt() 中，在 missing_desc 之后：
blocker_text = ""
if blockers:
    blocker_text = format_blockers_for_prompt(blockers)
    
# 注入位置：现有 "does not execute" 之后
f"""...when tested, {missing_desc} not execute.

COVERAGE ANALYSIS — Why these lines are not reached:
{blocker_text}

Use these insights to construct test inputs that specifically trigger the uncovered branches.
..."""
```

#### 1.4.5 DiagnosticIR 扩展

在 `DiagnosticIR` 中新增可选字段：

```python
coverage_blockers: Tuple[str, ...] = ()  # P5: blocker 描述列表
```

#### 1.4.6 CodeSegment 扩展

在 `CodeSegment` 中缓存 blockers：

```python
class CodeSegment:
    # 新增字段
    coverage_blockers: List[CoverageBlocker] = field(default_factory=list)
```

### 1.5 Prompt 输出示例

**Rust 示例**（from `similar` crate）:

```
COVERAGE ANALYSIS — Why these lines are not reached:

1. Line 156 (false branch of `if self.d_old.len() > self.d_new.len()`):
   - Condition: `self.d_old.len() > self.d_new.len()`
   - Currently: all tests have d_old shorter than d_new
   - To reach: construct a DiffOp where the old sequence is longer
   - Variable `self.d_old` comes from: field of `DiffableStr` struct

2. Line 203 (match arm `ChangeTag::Insert` of `match tag`):
   - Condition: `tag` equals `ChangeTag::Insert`
   - Currently: tests only exercise `Equal` and `Delete` variants
   - To reach: create a diff scenario with insertions
   - Variable `tag` comes from: return value of `DiffOp::tag()`
```

**Go 示例**:

```
COVERAGE ANALYSIS — Why these lines are not reached:

1. Line 89 (false branch of `if len(args) == 0`):
   - Condition: `len(args) == 0`
   - Currently: all tests pass non-empty args
   - To reach: call Execute() with empty argument slice
   - Variable `args` comes from: parameter of func `Execute(args []string)`
```

### 1.6 与 PALM 的差异

| 维度 | PALM | P5 (ours) |
|------|------|-----------|
| **分析深度** | 完整路径约束（SMT-like） | 最近控制条件 + 变量来源追溯 |
| **实现成本** | 重量级程序分析框架 | 100-200 行 tree-sitter 代码/语言 |
| **语言覆盖** | Rust only | Rust + Go + Python |
| **运行时信息** | 无 | 利用已有覆盖率数据（哪些分支已执行）|
| **与 Memory 协同** | 无 | Blocker hint + Recipe 联合注入 |
| **论文属性** | 静态分析系方法 | 轻量动态证据 + 可解释性 |

---

## 2. Memory 成功定义修正

### 2.1 问题

当前 `memory.record(ir, action, succeeded)` 中，`succeeded` 仅在**最终产生覆盖率增益**时为 True。导致所有编译类修复（如 autofix_imports 让代码从 fail → compile）的 success_rate 永远为 0。

### 2.2 修正方案

引入**分层成功**概念：

```python
class SuccessLevel(Enum):
    FULL = "full"           # 产生覆盖率增益 (G)
    PARTIAL = "partial"     # 编译通过但无增益 (U) 或修复后仍需 LLM
    COMPILE = "compile"     # 从编译失败恢复到编译通过
    NONE = "none"           # 完全失败 (F)
```

改动点:

```python
# coverup.py 中的 record 调用
# 当前：
memory.record(ir, action="tool_fix_imports", succeeded=False)  # 工具修复后仍最终失败

# 改为：
memory.record(ir, action="tool_fix_imports", succeeded_level=SuccessLevel.COMPILE)
```

Recipe 排序时考虑分层权重:

$$\text{success\_rate} = \frac{w_{\text{full}} \cdot n_{\text{full}} + w_{\text{partial}} \cdot n_{\text{partial}} + w_{\text{compile}} \cdot n_{\text{compile}}}{n_{\text{total}}}$$

建议权重: $w_{\text{full}}=1.0,\ w_{\text{partial}}=0.3,\ w_{\text{compile}}=0.5$

### 2.3 代码改动

| 文件 | 改动 |
|------|------|
| `agents/memory.py` | `Recipe` 新增 `compile_count`, `partial_count`; `record()` 接受 `SuccessLevel`; `success_rate` 用加权公式 |
| `coverup.py` | 所有 `memory.record()` 调用改为传 `succeeded_level` |
| 约 15 处调用需要更新 |

---

## 3. Planner 收益隔离：Wave-Baseline 实验设计

### 3.1 问题

当前 Agent vs Baseline 的对比中，Agent 使用波次调度，Baseline 使用一次性全量调度。reviewer 可以说 "+1.6pp 来自调度形态，不是 agent"。

### 3.2 解决方案：新增 Wave-Baseline 变体

```
wave-baseline: 使用 UCBPlanner 的 select_batch() 波次调度，
               但禁用 Memory + Repair + P5
               → 隔离"波次形态"的纯收益
```

CLI 实现：已有 `--no-agent-memory` + `--no-agent-repair`。只需 Planner 保留但 Memory/Repair 禁用。

实际命令：
```bash
# wave-baseline
--no-agent-memory --no-agent-repair
# (planner 仍启用，提供波次形态但无 recipe/repair 辅助)
```

### 3.3 完整消融矩阵

| 变体 | Planner | Memory | Repair | P5 | 隔离什么 |
|------|---------|--------|--------|----|---------|
| **full** | ✅ | ✅ | ✅ | ✅ | — |
| **no_p5** | ✅ | ✅ | ✅ | ❌ | P5 的增量贡献 |
| **no_memory** | ✅ | ❌ | ✅ | ✅ | Memory 的增量贡献 |
| **no_repair** | ✅ | ✅ | ❌ | ✅ | Repair 的增量贡献 |
| **wave_baseline** | ✅ | ❌ | ❌ | ❌ | 纯波次调度收益 |
| **baseline** | ❌ | ❌ | ❌ | ❌ | 原版 CoverUp |

这样可以计算：
- **波次调度纯收益** = wave_baseline - baseline
- **Memory 净收益** = full - no_memory
- **Repair 净收益** = full - no_repair
- **P5 净收益** = full - no_p5
- **Agent 总收益** = full - baseline
- **Agent 非调度收益** = full - wave_baseline

---

## 4. 实证补齐计划

### 4.1 项目选择（最小集: 15 个项目）

| # | 语言 | 项目 | LOC (src) | 当前覆盖率 | 来源 |
|---|------|------|-----------|-----------|------|
| 1 | Rust | similar | ~2k | 81% → 92.5% | 已验证 |
| 2 | Rust | semver | ~3k | ~75% | 已部署,待跑 |
| 3 | Rust | strsim-rs | ~0.5k | ~70% | 已部署,待跑 |
| 4 | Rust | regex-lite | ~3k | TBD | 中等复杂度 |
| 5 | Rust | once_cell | ~1k | TBD | 小型实用库 |
| 6 | Python | flask (core) | ~5k | ~90% | CoverUp 原文已用 |
| 7 | Python | click | ~5k | TBD | 本仓库已有 |
| 8 | Python | pydantic-core | ~3k | TBD | 类型验证库 |
| 9 | Python | httpx | ~4k | TBD | HTTP 客户端 |
| 10 | Python | attrs | ~2k | TBD | 数据类库 |
| 11 | Go | cobra | ~3k | 90.9% → 97.7% | 已验证 |
| 12 | Go | logrus | ~2k | TBD | 日志库 |
| 13 | Go | gjson | ~3k | TBD | JSON 解析 |
| 14 | Go | pflag | ~2k | TBD | 命令行标志 |
| 15 | Go | cast | ~2k | TBD | 类型转换 |

### 4.2 运行矩阵

| 维度 | 值 |
|------|---|
| 项目 | 15 |
| 变体 | 6 (full, no_p5, no_memory, no_repair, wave_baseline, baseline) |
| 重复 | 3 次 (temperature=0 + 不同 seed 或固定 seed 跑 3 次取方差) |
| **总运行次数** | **270 次** |

预估时间：每次 ~40min → 270 × 40min = 180 小时 ≈ 8 天（5 并发）。

### 4.3 统计方法

- Wilcoxon signed-rank test (配对非参数检验, n=15 per variant pair)
- Cliff's delta 效应量
- 95% 置信区间

---

## 5. 论文结构与贡献声明

### 5.1 标题建议

> **Closing the Coverage Gap: Agentic LLM Test Generation with Blocker Explanation**

或更学术：

> **From Missing Lines to Reachability Conditions: Agent-Guided Coverage-Driven Test Generation**

### 5.2 贡献声明（4 点，重新分级）

**Contribution 1 (核心方法创新): Coverage Blocker Explanation**

将 LLM 收到的反馈从 "cover lines X-Y" (where) 升级为
"line Y unreached because `guard(x>0)` at line X, where x comes from `parse()` at line W" (why + how)。
通过 tree-sitter/AST 提取守卫条件 + 变量来源追溯，生成结构化可执行到达条件。
首个将 **guard extraction + variable provenance tracing** 用于 LLM 测试生成引导的方法。
区别于 PALM 的完整路径约束分析，仅 ~150 LoC/语言，零额外运行时开销，原生跨语言 (Rust/Go/Python)。
**直接攻击 Useless (编译通过但无覆盖增益) 这一全行业痛点。**

**Contribution 2 (方法创新): Hierarchical Recipe Memory + Two-Phase Repair**

关键不是"有记忆"，而是 **action-diagnostic_signature-success_probability 三元组技能库**。
通过分层成功信号 (COMPILE → PARTIAL → FULL) 让系统学到"如何修到能跑"这个中间技能，
不仅看最终覆盖率。配合 tool-first repair (0 成本确定性修复 → LLM 回退) 形成**渐进式修复技能积累**。
数据支撑: 失败率下降 10-41%，API 费用下降 10-20%。

**Contribution 3 (系统贡献): CoverAgent-ML Framework**

语言无关 DiagnosticIR (13 类错误 × 6 阶段) + 5-module ablatable architecture。
含 UCB budget allocator + wave scheduling 作为预算分配策略（不声称新 bandit 算法，
重点是"将决策引入控制流 + 支持完整消融实验"）。

**Contribution 4 (实证): Cross-language Evaluation**

3 语言 × N 项目，完整消融矩阵，验证：
弱 LLM (DeepSeek, ~30× 便宜) + Agent ≥ 强 LLM (GPT-4o) + naive (Flask 上验证)。

### 5.3 论文结构

```
1. Introduction (1.5p)
   - 问题：LLM 测试生成的 coverage gap 问题
   - 现有局限：CoverUp 只说 where, PALM 重量级, ASTER 无在线学习
   - 我们的方法：IR + Blocker + Planner + Memory + Repair
   
2. Motivating Example (1p)
   - 用 similar crate 的一个段展示：
     a) CoverUp 给 missing line，LLM 生成编译通过但不涨覆盖的测试
     b) 加 blocker 后 LLM 精准构造输入
   
3. Approach (5p)
   3.1 Overview & Architecture (DiagnosticIR + 模块关系图)
   3.2 Coverage Blocker Explanation ← 主创新 (1.5p)
       3.2.1 Guard Predicate Extraction (tree-sitter/AST)
       3.2.2 Variable Origin Tracing
       3.2.3 Reachability Hint Generation
   3.3 Hierarchical Recipe Memory + Two-Phase Repair ← 第二创新 (1.5p)
       3.3.1 SuccessLevel 分层信号 (COMPILE/PARTIAL/FULL)
       3.3.2 Success-weighted Recipe Ranking
       3.3.3 Tool-first Deterministic Repair
   3.4 Budget-Aware Scheduling (系统贡献, 0.5p)
       UCB allocator + wave scheduling + plateau freeze
   
4. Implementation (1p)
   - 三语言后端差异
   - tree-sitter 集成
   
5. Evaluation (4p)
   5.1 Setup (15 projects, 6 variants, 270 runs)
   5.2 RQ1: Overall effectiveness (coverage + G + cost)
   5.3 RQ2: Ablation (每个组件贡献)
   5.4 RQ3: Cross-language generalization
   5.5 RQ4: Efficiency (token-per-coverage-gain)
   5.6 RQ5: Useless reduction (P5 的 U 降低效果)
   
6. Discussion (1p)
   - Threats to validity
   - Limitations
   
7. Related Work (1p)
   - CoverUp, RUG, PALM, ASTER + general LLM test gen
   
8. Conclusion (0.5p)
```

### 5.4 关键指标（论文中必须报告）

| 指标 | 说明 | 来源 |
|------|------|------|
| Line Coverage (%) | 最终行覆盖率 | cargo llvm-cov / slipcover / go test |
| Branch Coverage (%) | 最终分支覆盖率（Rust 需 nightly） | 同上 |
| Good (G) | 成功生成的测试数 | CoverUp 输出 |
| Failed (F) | 编译/运行失败的尝试数 | CoverUp 输出 |
| **Useless (U)** | 编译通过但无覆盖增益 | CoverUp 输出，**P5 核心指标** |
| Compile Pass Rate | G+U / (G+F+U) | 派生 |
| **Token Efficiency** | Coverage gain per 1k tokens | 派生，**效率核心指标** |
| Cost ($) | LLM API 费用 | CoverUp 输出 |
| Wall Time (s) | 总耗时 | CoverUp 输出 |
| Recipe Count | Memory 积累的 recipe 数 | Agent 统计 |
| Repair Success Rate | 工具修复成功率 | Agent 统计 |
| Blocker Accuracy | P5 blocker hint 的准确率 (人工标注子集) | **新增指标** |

### 5.5 关键曲线（图表）

1. **Coverage vs. Attempt** 曲线 — 每个变体的覆盖率随尝试次数的增长（证明 Planner 收敛更快）
2. **Useless Rate vs. Variant** 柱状图 — full vs no_p5 vs baseline（证明 P5 降低 U）
3. **Compile Pass Rate vs. Attempt** — Repair+Memory 在减少失败
4. **Token Efficiency** 箱线图 — 每种语言每种变体（15 项目 × 3 重复）
5. **Ablation Heatmap** — 每个组件在每种语言上的 delta coverage

---

## 6. 实现优先级排序 (更新后)

| 阶段 | 任务 | 工作量 | 优先级 | 状态 |
|------|------|--------|--------|------|
| **已完成** | P5 核心实现 (blocker.py, 727行) | — | — | ✅ 完成 |
| 已完成 | Rust/Go tree-sitter predicate 提取 | — | — | ✅ 完成 |
| 已完成 | Python AST predicate 提取 | — | — | ✅ 完成 |
| 已完成 | Prompt 注入 (3 个 prompter) | — | — | ✅ 完成 |
| 已完成 | Memory SuccessLevel 分层 | — | — | ✅ 完成 |
| 已完成 | TraceLogger 接入主循环 | — | — | ✅ 完成 |
| 已完成 | `--no-agent-blocker` CLI flag | — | — | ✅ 完成 |
| 已完成 | 跨语言实验 (4项目) | — | — | ✅ 完成 |
| **Phase A** | 自适应 Pass 控制 (min_passes) | 0.5 天 | ★★★★★ | 🔲 待做 |
| Phase A | 项目规模自适应 (exploration tuning) | 0.5 天 | ★★★★ | 🔲 待做 |
| Phase A | 在 fastrand/cobra 上验证修复 | 0.5 天 | ★★★★ | 🔲 待做 |
| **Phase B** | U 差异分析 + 精准重试策略 | 1 天 | ★★★★ | 🔲 待做 |
| Phase B | 跨段模式学习 | 1 天 | ★★★ | 🔲 待做 |
| Phase B | 自适应温度调节 | 0.5 天 | ★★★ | 🔲 待做 |
| **Phase C** | 实验自动化脚本 (run_experiments.py) | 1 天 | ★★★★★ | 🔲 待做 |
| Phase C | 结果分析脚本 (analyze_results.py) | 1 天 | ★★★★ | 🔲 待做 |
| Phase C | 部署 10-15 个项目环境 | 2 天 | ★★★★ | 🔲 待做 |
| Phase C | 运行完整消融矩阵 (270次) | 8 天(5并发) | ★★★★★ | 🔲 待做 |
| **Phase D** | 论文撰写 | 5-7 天 | ★★★★★ | 🔲 待做 |
| 合计 | | ~22 天 | | |

---

## 7. 风险与缓解

| 风险 | 概率 | 缓解 |
|------|------|------|
| P5 对 U 的降低不显著 | 中 | 即使 P5 贡献小，Planner+Memory 的消融仍可支撑论文；P5 可降级为 NIER 投稿 |
| 多语言实验中某些项目 CoverUp 基础覆盖率已很高 | 中 | 选择初始覆盖率 60-85% 的项目，留足提升空间 |
| 270 次实验耗时超预期 | 中 | 可先跑核心 3 变体（full/baseline/no_p5）× 10 项目 × 2 次 = 60 次，够初稿 |
| LLM API 费用过高 | 低 | 实际每次 ~$0.35-0.40 × 270 ≈ $100-110，可控 |
| Reviewer 认为"多语言=工程贡献" | 中 | P5 的方法学创新 + DiagnosticIR 的统一决策空间声明防御 |

---

## 8. 写作中的关键表述 (reviewer 防御)

### 8.1 关于"多语言"

> ❌ "We are the first multi-language LLM test generation system."
> ✅ "We present a unified agentic framework where all decision components (planner, memory, repair) operate exclusively on a language-agnostic DiagnosticIR, enabling principled budget allocation across heterogeneous toolchains."

### 8.2 关于 vs CoverUp

> ❌ "CoverUp only works for Python."  
> ✅ "CoverUp's iterative coverage feedback is effective but lacks (1) accumulated repair experience across segments, (2) principled budget allocation among segments, and (3) causal explanation of why specific lines remain uncovered."

### 8.3 关于 vs PALM

> ❌ "PALM is too heavyweight."  
> ✅ "PALM achieves impressive results through comprehensive path constraint analysis, but its approach is tightly coupled to Rust's type system and compilation pipeline. Our Coverage Blocker Explanation achieves a pragmatic middle ground: it extracts the immediate branching predicate and variable provenance using only tree-sitter, requiring ~150 LoC per language, while leveraging existing coverage data as dynamic evidence."

### 8.4 关于 Useless 上升

> "The increased Useless rate in the agent variant reveals a fundamental tension: the planner's exploration of harder segments leads to more compilable-but-non-covering tests. P5 directly addresses this by providing causal reachability hints, reducing Useless rate by X% (from Y to Z)."
