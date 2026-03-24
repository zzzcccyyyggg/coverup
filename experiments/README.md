# 实验目录

本目录包含 CoverUp 项目的所有实验相关文件，与核心源代码分离管理。

## 目录结构

```
experiments/
├── scripts/                    # 实验运行与分析脚本
│   ├── experiment_config.yaml  # 实验矩阵配置（9项目×5变体×3种子）
│   ├── run_experiments.py      # 主实验运行器
│   ├── analyze_log.py          # 日志分析（DiagnosticIR 统计）
│   └── analyze_results.py      # 结果后处理
│
├── baselines/                  # 覆盖率基线快照
│   ├── slipcover.json          # Flask 基线覆盖率
│   └── slipcover_click.json    # Click 基线覆盖率
│
├── docs/                       # 实验设计与结果文档
│   ├── experiment_design.md    # 实验设计方案
│   └── experiment-results.md   # 实验结果分析
│
├── results/                    # 实验结果输出（gitignored）
├── logs/                       # 实验日志输出（gitignored）
└── summary.csv                 # 汇总数据（gitignored）
```

## 运行实验

```bash
# 运行完整实验矩阵
python experiments/scripts/run_experiments.py

# 分析日志
python experiments/scripts/analyze_log.py

# 后处理结果
python experiments/scripts/analyze_results.py
```

## 实验配置

详见 [scripts/experiment_config.yaml](scripts/experiment_config.yaml)：
- **9 个基准项目**：Rust (similar, semver, strsim-rs) / Python (flask, click, pydantic-core) / Go (cobra, logrus, gjson)
- **5 种消融变体**：full / no_memory / no_repair / no_planner / baseline
- **3 个随机种子**：42, 123, 456
