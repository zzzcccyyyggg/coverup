# Experimental Chapter Plan

Date: 2026-03-26

## Core Judgment

当前论文的实验章节不应按照“谁的覆盖率更高”这一单线思路来设计，而应围绕论文真正的主张来组织。  
这篇论文的核心不是“又一个多语言测试生成器”，也不是“某个 prompt 更好”，而是：

> **Coverage-guided retry should become failure-layer-aware structured recovery.**

因此，实验章节的核心任务不是证明“我们在所有任务上都最好”，而是证明以下四件事：

1. 完整系统相对于简单重试基线，确实改变了恢复路径；
2. bounded tool-first fixpoint 不是摆设，而是有因果作用的系统机制；
3. 同一个控制闭环在不同语言上会面对不同主导失败层；
4. 在不夸大广泛领先的前提下，系统仍能在一部分代表性任务上体现终态收益与成本收益。

如果按这个目标设计，实验章节就会更贴近论文主张，也更能经得起审稿。

---

## 1. Recommended Chapter Structure

推荐将实验章节写成六个部分。

### 6.1 Experimental Questions

直接用四个研究问题组织全文：

- **RQ1 (Mechanism):** 与简单重试基线相比，完整系统是否改变了恢复路径？
- **RQ2 (Causality):** bounded tool-first fixpoint 和 reachability hints 分别贡献了什么？
- **RQ3 (Cross-language):** 在同一个控制闭环下，Python、Go、Rust 的主导失败层如何不同？
- **RQ4 (Efficiency):** 完整系统在取得终态收益时，代价和效率如何变化？

### 6.2 Compared Systems

这一节说明对比对象，只放真正有因果意义的系统。

### 6.3 Subjects and Workloads

分成两层：

- targeted slice set
- aggregated project suite

### 6.4 Metrics

强调 trace-derived metrics 是一等公民，而不是只报 coverage。

### 6.5 Experimental Protocol

统一模型、seed、repo tag、budget、工作目录、日志记录方式。

### 6.6 Results

结果顺序建议固定为：

1. 机制表  
2. paired baseline 表  
3. 聚合项目表  
4. failure-layer figure  
5. case study

---

## 2. What To Compare Against

在比较对象上，建议遵循一个基本原则：

> **coverage 必须强调，但对比对象必须按“公平性”和“可复现性”分层。**

也就是说，论文里当然要正面回答“覆盖率有没有提高”，但不应该为了看起来 baseline 很多，就把一堆任务定义不同、语言不同、模型不同、覆盖率口径不同的系统硬塞进同一张主结果表。

因此，比较对象建议分成三层：

1. **主文必须做的因果对比**：我们自己的 direct baselines 和 ablations  
2. **可以做的最近邻外部对比**：只在可公平复现的语言子集上做  
3. **只做定性定位的外部工作**：用于 related work 和 discussion，不做主文 headline 数值比较

## 2.1 Primary Direct Comparisons

以下对比是必须做的，因为它们直接支撑论文主张。

### A. Full System

这是论文的主系统，包含：

- reachability / blocker hints
- structured diagnosis
- bounded tool-first fixpoint
- language-specific operators
- 当前完整 orchestration

### B. Retry-Only Baseline

这是**最重要的直接基线**。  
它应该保留：

- 同一模型
- 同一 target selection
- 同一运行预算
- 同一验证后端

但禁用恢复机制，只保留“覆盖率驱动 + 模型重试”。

这是论文里最关键的比较，因为它回答的是：

> 如果没有 structured recovery，仅靠简单 retry，会发生什么？

这一组不只是机制基线，也是最关键的 coverage 基线。  
主文中关于 coverage 的 headline，最稳妥的写法应当是：

> 与 retry-only baseline 相比，完整系统是否取得了更高 final coverage、更大的 coverage delta，或者在相近覆盖率下显著减少了无效重试和成本。

### C. No-Fixpoint

这是最重要的 ablation。  
它用来隔离：

> bounded tool-first repair 到底是不是有用，还是完整系统的收益其实来自别的部分？

如果这一组不做，bounded fixpoint 很难成为稳定创新点。

### D. No-Blocker

这组比较用于回答：

> coverage 告诉我们“哪里没打到”，而 blocker/reachability hint 告诉我们“为什么可能没打到”，这个增强是否值得？

这组在论文里应作为第二主 ablation，而不是最主 headline。

## 2.2 Secondary Ablations

这些对比可以做，但不应抢主线。

### E. No-Memory

如果有预算可以做，但建议放在附录或 secondary table。  
理由是当前论文并不主打 memory，而是主打 structured recovery。

### F. No-Planner

同理，planner 不应作为主创新点，因此这组 ablation 可以保留，但不要写成实验主轴。

## 2.3 Prompt Comparison

由于当前仓库已经将 prompt family 收敛为 `baseline` 和 `advanced` 两类，实验里可以保留一个附加 sanity：

- `advanced + retry-only`
- `baseline + retry-only`

它的作用不是为了证明 prompt 是主贡献，而是为了回答：

> 我们的收益是不是仅仅来自 prompt 变强，而不是 recovery loop？

这一点建议写在附录，或者放在实验节最后的 sanity 说明中，不要喧宾夺主。

## 2.4 External Prior Work Comparisons

这里必须非常克制。

### 可以考虑做直接比较的

只有在满足以下条件时，才适合做主文中的直接数值比较：

- 仓库相同或高度重合；
- tag/revision 可对齐；
- 覆盖率口径一致；
- 模型配置可冻结；
- prior system 可真实复现。

在当前条件下，**唯一有机会尝试直接复现并放入主文的外部工作，是最接近的 Python coverage-guided 系统**。  
即便如此，也建议只在 Python 子集上作为附加 comparison，而不是整篇论文的 headline baseline。

更具体地说，建议如下：

### Python 子集：建议比较的外部工具

1. **最接近的 coverage-guided LLM 系统**
   - 这是 Python 子集里最应该比较的对象
   - 因为它与我们的问题设定最接近
   - 即使整篇论文不以它为中心，也建议至少在 Python 子集上尝试做一张附加表

2. **如果可稳定运行，可增加一个传统 Python 自动测试工具作为参考**
   - 这个对比的作用不是证明我们一定全面优于它
   - 而是说明：在同样的 Python 项目上，coverage-guided LLM recovery 与传统自动测试生成路径相比有何差异
   - 但前提是工具能在同一项目、同一覆盖率口径下稳定运行

### Rust 子集：建议比较的外部工具

1. **PALM**
   - 如果能在 overlapping Rust repositories 上公平复现，这是最有价值的 Rust 外部对比
   - 原因是它与“程序分析 + LLM + coverage/测试生成”最接近

2. **RUG**
   - 如果 artifact 可运行、仓库可对齐、口径可统一，可以作为 Rust 子集的第二外部工具
   - 但不要在无法对齐的情况下强行进主表

### Go 子集

Go 目前更现实的做法是：

- 不强求外部工具主表比较
- 先把 `retry-only baseline / no-fixpoint / no-blocker` 做扎实
- 再在 discussion 中说明：当前公开、可复现、与任务定义完全一致的 Go 外部系统有限

这样写反而更稳，不会因为不公平比较被 reviewer 追着打。

### 不建议做主文直接数值比较的

以下工作更适合在 related work 或 discussion 中做方法层面的定位，而不适合直接放在主结果表里做“数值对打”：

- ASTER
- PALM
- RUG
- Panta
- CodaMOSA
- TestGen-LLM / Meta industrial work

原因很明确：

- 任务定义不同；
- 支持语言不同；
- 覆盖率定义不同；
- 使用模型和时间点不同；
- 很多系统难以完全重现。

因此，实验章节应以**我们自己可控、可复现的 direct baselines 和 ablations**为主，外部工作用来做叙事定位，而不是冒险做不公平比较。

## 2.5 Recommended Coverage Story

覆盖率必须强调，但写法要避免变成“只有 coverage 一个数字”。

建议在主文里把 coverage 放在三个层面上强调：

### A. Aggregate Project Coverage

这是 reviewer 第一眼最想看到的。  
每个主变体都报告：

- initial coverage
- final coverage
- absolute delta（百分点）

### B. Coverage at Fixed Budget

如果预算允许，建议在 aggregated suite 中固定：

- 相同 max attempts
- 相同模型
- 相同时间或 token 上限

然后比较 coverage。  
这样可以更公平地说明完整系统不是靠“多花更多代价”换来的结果。

### C. Cost-Normalized Coverage Gain

建议至少报告一个派生指标：

- `coverage delta / dollar`
  或
- `cost per terminal G`

这能把“效果”和“代价”联系起来。

### D. Coverage 不是唯一 headline

最终主文里最理想的 headline 结构应当是：

1. 先用机制表说明 recovery loop 真实存在
2. 再用 aggregate table 说明 coverage 确实提高或更高效

而不是反过来只讲 coverage，再让机制沦为附属解释

---

## 3. Recommended Experimental Design

## 3.1 Two-Track Design

整个实验章节建议采用双轨设计。

### Track A: Mechanism-Oriented Slice Study

目标：

- 证明 recovery loop 是真实存在的系统机制；
- 证明它会改变恢复路径；
- 证明不同语言会进入不同 recovery class。

这一轨的评价重点不是大规模 coverage，而是：

- observed path
- recovery class
- repair engagement
- average repair passes
- fixpoint exhaustion
- dominant failure family

这是最契合当前论文主张的一轨，也是当前已有证据最强的一轨。

### Track B: Small Aggregated Project Suite

目标：

- 证明 mechanism story 不只是个别 hand-picked case；
- 给出 project-level 的终态效果、成本和效率结果。

这一轨的作用是补“论文像样性”，但不需要追求大而全。

---

## 3.2 Targeted Slice Set

建议主文最小 slice set 为 **8 个**，分布如下：

- Python：2 个
- Go：4 个
- Rust：2 个

推荐构成：

### Python

1. 一个 repair-assisted positive
2. 一个 repair-engaged negative 或 harder positive

原因：

- Python 目前是 strongest positive evidence
- 需要既有强正例，也有边界样例

### Go

1. 一个 repair-assisted positive
2. 一个 prompt-first positive
3. 一个 repair-engaged negative
4. 一个 behavior-semantics harder slice

原因：

- Go 当前最能体现 recovery classes 的丰富性
- 同时也是最适合展示“同一个 loop 可以出现多种恢复路径”的语言

### Rust

1. 一个 prompt-first positive paired contrast
2. 一个 harder negative 或 repair-engaged slice

原因：

- Rust 是 hardest language
- 论文不应假装 Rust 已成熟
- 但也必须避免 Rust 只剩一个正例对比点

## 3.3 Aggregated Project Suite

建议采用**主文 6 项目、附录扩展到 9 项目**的设计。

### 主文最小套件（推荐）

- Python: `click`, `flask`
- Go: `cobra`, `gjson` 或 `logrus`
- Rust: `similar`, `strsim-rs`

理由：

- 每种语言两个项目，结构均衡；
- 既有 CLI / framework / library 类型差异；
- 当前代码和实验脚本对这些项目已有较多积累。

### 附录扩展套件（可选）

在主文 6 项目稳定后，再扩到当前配置里的 9 项目。

这样做的好处是：

- 先保证主文结果能跑完、能讲清；
- 再把更大规模矩阵作为增强证据，而不是把自己卡死在 162 runs 上。

---

## 4. Metrics

## 4.1 Primary Metrics

实验章节的主指标建议如下。

### Terminal G / F / U

必须用 **trace-derived terminal outcomes**，而不是直接用 summary raw counters。  
原因是 bounded fixpoint 可能在一次外部 attempt 中产生多个内部 failure 事件，如果直接用 raw counters 会误导。

### Final Coverage

- line coverage
- branch coverage（如果语言后端支持且口径稳定）

Coverage 应作为主结果之一，但不能是唯一 headline。

### Recovery Class Distribution

每种配置下，报告有多少 slice 属于：

- repair-assisted positive
- prompt-first positive
- repair-engaged negative
- llm-only negative

这是当前论文最该突出的指标。

### Repair Engagement Rate

报告：

- 有多少终态路径真正进入了 `tool_repair+llm`
- 占所有 slices 的比例

### Average Repair Passes

报告 repair 介入后平均跑了几轮 pass。  
这有助于解释 fixpoint 是否只是 nominal feature，还是实际在工作。

### Fixpoint Exhaustion Rate

如果 fixpoint 经常 exhaustion 但不产生成果，这本身就是重要信号。

### Cost and Cost Per Good

建议保留：

- total cost
- cost per terminal G

因为 structured recovery 的一个重要潜台词是“减少浪费的 retry”。

## 4.2 Secondary Metrics

- Wall time
- Failure-family composition
- Memory lesson count
- Planner pulls / target reallocation statistics（如保留）

这些指标不应成为 headline，但可用于支撑分析。

---

## 5. Experimental Protocol

## 5.1 Freeze Conditions

所有 direct comparisons 必须共享以下条件：

- 同一 repository tag / commit
- 同一模型
- 同一温度
- 同一最大尝试次数
- 同一 target selection policy
- 同一验证后端
- 同一工作目录清理方式

如果这些条件不一致，实验很容易被 reviewer 质疑为不可比。

## 5.2 Model Policy

推荐只选一个主模型作为论文主文模型，并在文中写清：

- 模型名
- 接口提供方
- 冻结日期

例如：固定为某个模型版本，并标注“as of March 26, 2026”。  
原因是托管模型行为会漂移，不写清日期容易让结果失真。

## 5.3 Seed Policy

建议：

- aggregated suite：每个项目 3 seeds
- targeted slices：每个 paired contrast 至少 2--3 次重复

如果成本不足，优先保证：

1. paired slice 的复验
2. 6 项目主套件

不要优先铺很大的矩阵而失去关键 paired evidence。

## 5.4 Workspace Hygiene

必须保证：

- 每次 run 都从干净 repo 解压或 clean checkout 开始
- 删除历史生成测试
- 固定依赖版本
- 保存 raw stdout、trace JSONL、summary JSON

尤其是当前项目已经出现过“历史生成测试污染后续 baseline”的情况，因此 hygiene 必须写进 protocol。

---

## 6. How To Write the Results

## 6.1 Table Order

主文建议按以下顺序放结果。

### Table 1: Mechanism Table

字段建议：

- Slice
- Recovery Class
- Observed Path
- RepairEng
- AvgPass
- FixExh
- Representative Fixes

这是第一张主表，因为它最贴合论文主张。

### Table 2: Paired Baseline Sanity

字段建议：

- Slice
- Full Path
- Full Class
- Baseline Path
- Baseline Class
- Interpretation

这一张表负责回答：

> 哪些结果真的依赖完整 recovery loop？

### Table 3: Aggregate Project Outcomes

字段建议：

- Project
- Variant
- Initial Coverage
- Final Coverage
- Delta (pp)
- Terminal G/F/U
- Cost
- Cost per G

### Table 4: Main Ablation Summary

建议只放：

- Full
- Retry-only baseline
- No-fixpoint
- No-blocker

Memory / planner 相关放 appendix。

## 6.2 Figure Order

### Figure 1: Recovery Class Distribution

按语言分组，展示不同 class 的数量或比例。  
这会直接支撑“论文主评价对象是 recovery path”。

### Figure 2: Failure-Family Composition by Language

展示 Python / Go / Rust 各自更常见的 failure layers。  
这张图是 cross-language claim 的核心图。

### Figure 3: Cost vs Useful Outcome

比如散点图或条形图，展示 full 与 baseline / no-fixpoint 在成本与 terminal G 上的权衡。

### Figure 4: Coverage Delta by Project

建议增加一张最直接的 coverage 图。  
每个项目一组柱：

- retry-only baseline
- full
- no-fixpoint
- no-blocker

纵轴用 `Delta over initial coverage (pp)`。  
这张图会显著提升 reviewer 对“效果”的直觉把握。

## 6.3 Case Studies

实验章节最后建议保留两个 case study：

1. 一个 repair-assisted positive  
2. 一个 harder repair-engaged negative

原因：

- 正例说明系统能带来结果；
- 负例说明系统的边界和失败前沿；
- 两者合在一起，论文更可信。

---

## 7. What Not To Do

## 7.1 不要让实验章节变成“比谁 coverage 高”

这是最危险的写法，因为你现在最强的贡献不是绝对 coverage，而是 recovery mechanism。

更准确地说：

- coverage 必须强调
- 但不能只强调 coverage

最佳做法是让 coverage 成为结果 headline，让 recovery path 成为因果解释 headline。

## 7.2 不要把所有成功都归因于 full system

像 `ResetFlags` 这种 prompt-first positive 必须如实写。  
这不是坏事，恰恰能增强可信度。

## 7.3 不要用不公平的 prior-work 数字做 headline

如果 repo、模型、coverage 口径对不上，就不要在主文里硬做数值对比。

## 7.4 不要让 planner / memory 抢主线

它们可以出现，但不应盖过：

- failure-layer-aware recovery
- DiagnosticIR
- bounded tool-first fixpoint

---

## 8. Minimal Submission-Ready Experimental Package

如果以“最小可投稿实验包”为目标，我建议按下面这个标准推进。

## Must Have

1. 8 个 targeted slices 的 mechanism table
2. 5 个 paired baseline contrasts
3. 6 项目 × 3 seeds × 4 variants 的 aggregate suite
4. 1 张 recovery class 分布图
5. 1 张 cross-language failure-family 图
6. 1 张 per-project coverage delta 图

## Highly Recommended External Comparison

如果时间和复现条件允许，再补以下对比：

1. Python 子集上与最接近的 prior coverage-guided LLM system 做一张附加表
2. Rust 子集上与 PALM 或 RUG 做一张附加表

但这两类都不应阻塞主文主实验的完成

## Strong Additions

1. 9 项目扩展矩阵
2. `no-memory` ablation
3. prompt sanity appendix
4. 一个可直接复现的 prior Python system comparison

## Can Be Omitted If Needed

1. planner headline analysis
2. 大而全的 external system bake-off
3. 太多不稳定的 secondary metrics

---

## 9. Most Important Next Step

下一步最值得做的事情不是继续泛化讨论，而是：

> **把实验章节真正冻结成“两轨四问”的结构，然后按这个结构只补最值钱的数据。**

更具体地说：

1. 先把 `Full / Retry-only / No-fixpoint / No-blocker` 这四组定为主文主矩阵；
2. 先跑 6 项目主套件；
3. 先补齐 8 个 targeted slices；
4. 然后再考虑更大矩阵和额外 prior comparison。

这条路径最符合当前论文的创新点，也最有机会把实验章节做成“可 defend”的样子，而不是做成“表很多但主线不清”的结果堆砌。
