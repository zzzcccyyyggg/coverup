# CoverAgent-ML 投稿恢复计划

> 目标：把当前“已有原型 + 初步文档 + 零散结果”推进成一篇经得起系统/软件工程审稿的论文。
>
> 约束：以可投稿性为最高目标，而不是以继续堆功能为目标。

## 0. 项目重建

### 0.1 当前项目到底是什么

用一句话概括：

> 这是一个建立在 CoverUp 之上的、多语言、带在线闭环控制的 LLM 测试生成系统，试图把“基于 missing coverage 的盲目重试”升级为“带 reachability hint、错误归因、修复和经验积累的自适应生成”。

### 0.2 已被代码和仓库材料支持的事实

- 已有可运行的系统原型，而不是纯设计稿。
  - 核心 agent 模块已经在代码中实现并接入主循环：
    - `DiagnosticIR`
    - `ReflectiveMemory`
    - `RepairOrchestrator`
    - `UCBPlanner`
    - `CoverageBlocker`
    - `TraceLogger`
- 系统当前明确支持 Python / Go / Rust 三种语言。
- `CoverageBlocker` 已真实接入 prompt 注入，而不是 roadmap 中的未来工作。
- `Planner` 的 `min_passes` 与 size-adaptive 参数也已经在主循环中使用。
- 仓库中已有实验脚本、论文草图、系统文档，以及本地 related-work 参考库。

### 0.3 根据现有信息做出的合理推断

- 当前最自然的投稿方向是软件工程/自动化测试，而不是安全。
  - 原因：项目没有明确的 threat model、attack surface、security objective 或安全 benchmark。
- 最可能站得住的主贡献不是“agent”这个词，而是：
  - 从 `where not covered` 到 `why/how reachable` 的 prompt 信息升级；
  - 用统一诊断 IR 驱动 repair / memory / planning；
  - 在多语言框架下验证这种闭环。
- 如果继续把 `Planner/UCB` 当主要 novelty，容易被审稿人判定为系统工程细节，而非研究贡献。

### 0.4 需要进一步实验验证的猜想

- `CoverageBlocker` 是否显著降低 useless tests，而不是只是“看起来更合理”。
- `Memory + Repair` 是否稳定降低失败率，并且这种降低能转化为最终 coverage 收益。
- “弱模型 + 更强控制流”是否能在公平口径下稳定接近或超过“强模型 + 朴素流程”。
- 多语言是否真的形成优势，还是只是“功能上支持三种语言，但每种证据都偏弱”。

### 0.5 明显高风险或不建议主打的方向

- 主打“bandit/planner 算法创新”。
- 继续混用不同 coverage 度量口径做强比较。
- 把 coverage gain 直接包装成 bug-finding 或 test quality 提升。
- 在没有 blocker 消融的情况下，把 blocker 写成核心贡献。

## 1. 文献重新定位

已下载相关论文见：

- [related-work README](/home/zzzccc/coverup/paper/related-work/README.md)
- [related-work PDFs](/home/zzzccc/coverup/paper/related-work/pdfs)

### 1.1 最关键的对比对象

#### A. 直接系统祖先 / 同类基线

- CoverUp
  - 你的系统基础框架。
  - 直接回答“agent 层是否真的带来增益”。

- CodaMOSA
  - 传统 hybrid baseline。
  - 适合作为远端背景，不适合作为最主要的 direct competitor。

#### B. 最危险的直接 novelty 竞争者

- PALM
  - 通过程序分析抽取路径/约束，引导 Rust 测试生成。
  - 对你的 `Blocker` 故事威胁最大。
  - 如果我们继续声称“首个 why/how reachability guidance”，很容易被打穿。

- SymPrompt
  - 多阶段、coverage-guided、code-aware prompting。
  - 它说明“把问题分解给 LLM + 路径/上下文引导”不是空白。

- Panta
  - 强调 iterative hybrid analysis。
  - 会削弱“analysis + feedback loop”作为广义 novelty 的说法。

#### C. 会削弱“多语言本身很新”的工作

- ASTER
  - 已经是 multi-language LLM unit test generation。
  - 所以“我们支持多语言”只能作为系统价值，不能单独构成主 novelty。

#### D. 会迫使我们收紧 claim 的工作

- TestGen-LLM
  - 强工业闭环、过滤保障、已有测试增量改进。
  - 说明“改进 existing tests + assured filtering”已有强先例。

- Mutation-Guided LLM-based Test Generation at Meta
  - 说明 alternative feedback signal 是 mutation，不只是 coverage。
  - 审稿人可能问：为什么 coverage signal 比 mutation 更合适？

- Design choices made by LLM-based test generators prevent them from finding bugs
  - 这是必须正面处理的批判。
  - 它直接攻击“通过测试 + 增 coverage”的系统可能会把 bug 固化到 suite 中。

## 2. 核心判断

### 2.1 目前最可投稿的主线

最可行主线：

> 一个轻量、跨语言的 reachability-aware + diagnosis-driven test generation loop。

更具体地说，论文应该主打：

1. `CoverageBlocker`
   - 但措辞必须收紧为：
   - “lightweight reachability explanation”
   - 而不是“完整路径约束分析”或“首个 why/how 方法”

2. `DiagnosticIR + Memory + Repair`
   - 这是比 planner 更容易形成闭环贡献的部分。
   - 因为它解释了系统为什么能减少失败和重试。

3. Planner 仅作为系统调度补充
   - 贡献表述降级为：
   - “budget-aware control integration”
   - 不声称新 bandit 算法。

### 2.2 最不建议的主线

- “agent makes weak LLM beat strong LLM”
  - 可以作为观察，但不能做论文主 claim。
  - 因为很容易被版本、数据集、运行预算、公平性问题攻击。

- “cross-language framework”作为唯一主卖点
  - ASTER 已经让这个说法不够强。

## 3. 可投稿性审计

### 3.1 Novelty Audit

#### 当前可以保留的点

- 比 CoverUp 更强的在线闭环控制。
- 比 PALM 更轻量、低成本、可跨语言的 reachability hint。
- 比单纯 repair/memory 方法更统一的 IR 驱动控制。

#### 当前不能直接保留的点

- “first analysis-guided LLM test generation”
- “first multi-language LLM unit test generation”
- “first to provide why/how guidance”

这些说法都需要改弱，或限定范围。

### 3.2 Methodology Audit

#### 优点

- 系统有清晰控制回路。
- 模块边界明确，适合做 ablation。
- 多语言共享控制层，这点实现上有说服力。

#### 短板

- 文档与代码状态不完全同步。
- blocker/memory/planner 的贡献边界还没有被实验隔离清楚。
- 当前很多叙事是“模块故事”，还不是“研究问题 -> 方法 -> 证据 -> claim”闭环。

### 3.3 Evaluation Audit

这是当前最大短板。

#### 已知问题

- 实验结果主要体现在说明文档中，而不是仓库内可复现结果。
- 当前 runner 存在明显可信度问题：
  - seed 被声明但未真正驱动系统；
  - coverage 解析逻辑与实际输出不一致；
  - 尚未把 blocker 放入正式消融矩阵。
- 当前公开叙事中存在多种不公平或不可比对比：
  - 不同模型；
  - 不同项目版本；
  - 不同 coverage 度量；
  - generated-only vs incremental coverage。

#### 缺失的关键证据

- `no_blocker` ablation
- 多 seed 重复
- 项目内 trace 对照分析
- 至少一个“质量/有效性”补充视角，而不是只有 coverage

### 3.4 Writing Audit

#### 当前写作问题

- 故事线过多：
  - blocker
  - memory
  - repair
  - planner
  - multi-language
  - cheap model vs strong model
- 这样会让 reviewer 觉得系统像 feature bundle，而不是研究主张。

#### 推荐改法

- 论文只保留一条主线和一条副线：
  - 主线：reachability-aware guidance
  - 副线：diagnosis-driven repair/memory loop
- planner 放系统节，不再争主位。

## 4. 具体修改计划

### Phase 0: 先修“证据链”，不是先修功能

#### P0.1 修实验脚本可信度

目标：

- 让每次运行的输入、随机性、输出指标都可信。

应做：

- 修 `run_experiments.py` 中 seed 形同虚设的问题。
- 修 coverage 解析和实际程序输出不一致的问题。
- 把 trace、result、log 三类产物统一保存。
- 明确每个运行的项目版本、模型、参数、时间预算。

#### P0.2 补 blocker 消融

目标：

- 如果 blocker 是主贡献，就必须能单独回答：
  - 是否降低 useless；
  - 是否带来 coverage 提升；
  - 是否在不同语言上效果一致。

应做：

- 在实验配置里加入 `no_blocker`。
- 形成最小矩阵：
  - `baseline`
  - `full`
  - `no_blocker`
  - `no_memory`

#### P0.3 固化一个小而硬的可复现实验切片

建议优先项目：

- Flask
- similar
- cobra

原因：

- 分别覆盖 Python / Rust / Go；
- 当前仓库已有叙事基础；
- 能快速判断多语言 story 是否还能成立。

### Phase 1: 收紧 claim

#### P1.1 删弱或降格的 claim

- 删除“weak LLM beats strong LLM”式 headline。
- 删除把 planner 当核心方法创新的表述。
- 删除所有隐含“bug-finding stronger”但没证据支持的句子。

#### P1.2 重写 contribution list

建议改成：

1. 轻量跨语言 reachability explanation
2. diagnosis-driven repair/memory loop
3. language-agnostic integration with ablation support
4. cross-language empirical study

### Phase 2: 重新组织实验问题

建议 RQ 重写为：

- RQ1: `full` 相对 `baseline` 是否提升最终 coverage / efficiency？
- RQ2: `blocker` 是否显著降低 useless attempts？
- RQ3: `memory + repair` 是否显著降低 failed attempts，并提升成功转化率？
- RQ4: 增益是否跨语言稳定，还是只在复杂项目中成立？
- RQ5: 代价是什么？时间、token、以及可能的 quality 风险是什么？

### Phase 3: 补一个“质量约束”视角

这是为了主动应对批判性审稿。

可选方式：

- 不声称 bug-finding，但加入：
  - flaky rate
  - compile/pass/acceptance filter
  - 失败/无效/通过但无增益占比
- 或加入小规模人工审查：
  - 抽样检查部分新增测试是否只是过拟合当前实现

如果做不到，不要写强质量 claim。

## 5. 任务优先级

### 第一优先级

- 修实验 runner
- 加 `no_blocker`
- 跑最小可信矩阵

### 第二优先级

- 基于真实结果决定 blocker 是否继续做主线
- 重写 paper outline 和 contribution list

### 第三优先级

- 再决定是否要继续强化 planner 或加入额外质量评估

## 6. 决策门槛

### 如果出现以下结果，建议继续主打 blocker

- `no_blocker` 明显提升 useless rate
- coverage 也有稳定增益
- 至少在两种语言上方向一致

### 如果出现以下结果，建议降 blocker、主打 repair/memory

- blocker 只改善个别项目
- useless 降了但 coverage 不升
- 提升主要来自更少失败和更高编译通过率

### 如果出现以下结果，建议整体降稿目标或重构论文问题

- `full` 对 `baseline` 在多数项目上没有稳定优势
- 多次运行波动很大
- 多语言 story 无法形成一致趋势

## 7. 下一步最值得做的事情

唯一最值得立即做的事情：

> 先把实验系统修到“能产生可信消融结果”，尤其是 `no_blocker`、seed、coverage 输出解析和 trace 产物保存。

在这之前，不建议继续扩模块，也不建议继续强化论文措辞。
