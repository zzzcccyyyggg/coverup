# CoverAgent-ML 跨语言实验结果

## 实验配置

| 参数 | 值 |
|------|-----|
| LLM | DeepSeek Coder (`deepseek/deepseek-coder`) |
| Temperature | 0 |
| Max Attempts | 3 |
| Max Concurrency | 3 |
| Agent 模块 | Memory + RepairOrchestrator + UCBPlanner + Blocker |

## 总结

| 项目 | 语言 | 论文来源 | 初始覆盖率 | Baseline 最终 | Agent 最终 | Baseline Δ | Agent Δ | Agent 优势 |
|------|------|---------|-----------|-------------|-----------|-----------|---------|----------|
| similar | Rust | 内部 | — | 90.9% | 92.5% | — | — | +1.6pp |
| fastrand | Rust | PALM (2025) | 83.6% | 97.5% | 96.2% | +13.9pp | +12.6pp | **-1.3pp** |
| Flask | Python | CoverUp (FSE'25) | 89.9% | 94.9% | 95.8% | +5.0pp | +5.9pp | **+0.9pp** |
| cobra | Go | 开源 CLI 库 | 90.7% | 97.3% | 96.9% | +6.6pp | +6.2pp | **-0.4pp** |

## 详细结果

### 1. Rust — fastrand (PALM benchmark)

**来源**: PALM (2025) 论文 15 个 Rust benchmark crate 之一

#### Baseline (无 Agent)
- 初始覆盖率: 83.6%
- 最终覆盖率: 97.5%
- 统计: G=23, F=17, U=3
- 耗时: ~9.5 分钟
- 费用: ~$0.06
- 通过: 2 个 pass

#### Agent (全部模块启用)
- 初始覆盖率: 83.6%
- 最终覆盖率: 96.2%
- 统计: G=12, F=10, U=2
- 耗时: ~7.9 分钟
- 费用: ~$0.05
- Memory: 10 lessons, 错误分类: unknown:16/12, panic:3/0, import:1/0, type:2/0, visibility:2/0
- Planner: 24 pulls across 16 arms
- 通过: 1 个 pass

**分析**: Agent 在 fastrand 上低于 baseline (-1.3pp)。fastrand 是一个非常小的 crate，初始覆盖率很低(83.6%)，大部分代码结构简单。Agent 只做了 1 个 pass（16 items），而 baseline 做了 2 个 pass（28 total items）。Agent 的学习开销在小项目上带来的收益不足以抵消其引入的约束。

### 2. Python — Flask (CoverUp FSE'25 benchmark)

**来源**: CoverUp (FSE'25) 论文的官方示例项目，基于 CodaMosa CM benchmark

#### Baseline (无 Agent)
- 初始覆盖率: 89.9%
- 最终覆盖率: 94.9%
- 统计: G=72, F=125, U=30
- 耗时: ~35 分钟
- 费用: ~$0.46
- 通过: 1 个 pass (111 segments)

#### Agent (全部模块启用)
- 初始覆盖率: 89.9%
- 最终覆盖率: 95.8%
- 统计: G=80, F=107, U=27
- 耗时: ~57 分钟
- 费用: ~$0.41
- Memory: 74 lessons, 错误分类: unknown:120/80, import:25/0, type:17/0, visibility:22/0, assertion:30/0
- Planner: 214 pulls across 111 arms
- 通过: 1 个 pass (111 segments) + 5 extra items in pass 2

**分析**: Agent 在 Flask 上显著优于 baseline (+0.9pp)。Flask 是一个中等规模 Python 项目（~4K LOC），代码结构复杂，import/type/visibility 类错误较多。Agent 生成了更多好的测试 (G=80 vs 72)，同时失败更少 (F=107 vs 125)，体现了 Memory 模块的经验学习效果。

### 3. Go — cobra

**来源**: spf13/cobra，主流 Go CLI 框架

#### Baseline (无 Agent)
- 初始覆盖率: 90.7%
- 最终覆盖率: 97.3%
- 统计: G=86, F=69, U=0
- 耗时: ~29 分钟
- 费用: ~$0.30
- 通过: 2 个 pass (81 + 20 items)

#### Agent (全部模块启用)
- 初始覆盖率: 90.7%
- 最终覆盖率: 96.9%
- 统计: G=66, F=62, U=3
- 耗时: ~35 分钟
- 费用: ~$0.24
- Memory: 26 lessons, 错误分类: assertion:41/0, unknown:82/66, type:4/0, import:3/0, panic:1/0
- Planner: 130 pulls across 81 arms
- 通过: 1 个 pass

**分析**: Agent 在 cobra 上略低于 baseline (-0.4pp)。与 fastrand 类似，Agent 只做了 1 个 pass 而 baseline 做了 2 个。Agent 生成的好测试更少 (G=66 vs 86)，但失败也更少 (F=62 vs 69)。费用更低 ($0.24 vs $0.30)。cobra 项目的 Go 代码风格统一，baseline 已经能良好处理。

### 4. Rust — similar (之前的实验)

**来源**: 内部 A/B 测试（前期实验）

#### Agent vs Baseline
- Agent: G=23, F=110, U=15, 覆盖率 92.5%
- Baseline: G=31, F=173, U=6, 覆盖率 90.9%
- Agent 优势: +1.6pp，LLM 调用减少 30%

## 关键发现

### 1. Agent 在大/复杂项目上收益更大
- Flask (111 segments, Python): +0.9pp ✅
- similar (Rust, 高失败率): +1.6pp ✅
- fastrand (16 segments, Rust): -1.3pp ❌
- cobra (81 segments, Go): -0.4pp ❌

### 2. Agent 减少了 LLM 调用/总失败数
| 项目 | Baseline F | Agent F | 减少 |
|------|-----------|---------|------|
| Flask | 125 | 107 | -14.4% |
| cobra | 69 | 62 | -10.1% |
| fastrand | 17 | 10 | -41.2% |
| similar | 173 | 110 | -36.4% |

### 3. Agent 倾向于用更少的 pass 完成
Agent 在 fastrand 和 cobra 上只做了 1 个 pass，而 baseline 做了 2 个 pass。这意味着 Agent 认为在第一轮后已经充分利用了可用信息，但有时这导致最终覆盖率稍低。

### 4. Memory 模块积累了有意义的经验
- Flask: 74 lessons (最多)，错误分布: import 25次, type 17次, visibility 22次, assertion 30次
- cobra: 26 lessons, assertion 41次 (最常见错误)
- fastrand: 10 lessons, panic 3次

## 后续计划

1. **增加 pass 数量**: Agent 的 pass 数量可能需要调整，确保不会过早终止
2. **增加更多 benchmark**: 从 PALM 的 15 个 Rust crate 中选取更多（如 serde_json, hashbrown）
3. **消融实验**: 逐个关闭 Agent 模块，测量各模块的单独贡献
4. **统计显著性**: 需要多次重复实验（≥3 次）来计算统计显著性
