# Go Generation & Testing Updates

This document records all changes made to improve CoverUp's Go language support.

---

## Phase 2: Go Backend Major Enhancement (2026-02)

### 新增模块：`go_codeinfo.py` — Go 静态分析引擎

新增 `src/coverup/go_codeinfo.py`，对标 Python 的 `codeinfo.py`，为 Go 提供完整的静态分析能力：

| 函数 | 功能 |
|------|------|
| `get_info_go(file, name)` | 符号查询：支持 `FuncName`、`TypeName`、`TypeName.Method`、`pkg.Symbol` 格式 |
| `infer_branches(path, executed, missing)` | 分析 `if/else`、`switch/case`、`select` 推断分支覆盖 |
| `extract_receiver_type(node, source)` | 从方法声明中提取接收者类型名 |
| `find_type_definition(root, source, name)` | 查找 struct / interface 的定义源码 |
| `_collect_methods_for_type(dir, type_name)` | 收集某类型在同包中的所有方法签名 |

**符号查找策略：**
1. 先在当前文件用 tree-sitter 搜索（函数、类型、const/var）
2. 再搜索同包中其他 `.go` 文件
3. 最终 fallback 到 `go doc` 命令（支持标准库和第三方包）

### `go_backend.py` 更新

1. **增强代码分段** — `_find_enclosing_function` → `_find_enclosing_node`
   - 新增支持 `type_declaration`（struct/interface）、`var_declaration`、`const_declaration`
   - 大型 type 声明会尝试找到更小的内部节点以遵守 `line_limit`

2. **分支覆盖推断** — `_segments_for_file` 现在调用 `infer_branches()`
   - 将推断的 `missing_branches` 写入 `CodeSegment`，供 Prompt 使用
   - 分支的源/目标行加入 `lines_of_interest`

3. **接收者类型上下文** — 新增 `_get_receiver_context()`
   - 当 segment 是方法声明时，自动将接收者 struct 的类型定义行范围附加到 `context`
   - LLM 在代码摘录中能看到 struct 字段定义

4. **错误输出清洗** — `format_test_error()` 完全重写
   - 只保留编译错误、panic、测试失败、断言信息等关键行
   - 限制最多 40 行，对超出部分显示 omitted 计数

5. **`go mod tidy` 后自动重试**
   - 检测到 `no required module provides package` 时执行 `go mod tidy`
   - tidy 成功后立即重新执行 `go test`，而不是等待下次迭代

6. **`parse_go_cover_profile` 增加分支推断**
   - 解析覆盖率后调用 `infer_branches()` 为每个文件计算分支覆盖
   - 返回数据中 `branch_coverage` 设为 `True`

### `gpt_go_v1.py` 完全重写

1. **`get_info` 工具函数** — 首次为 Go prompt 暴露工具函数
   - 支持 `TypeName`、`TypeName.Method`、`pkg.Symbol` 格式
   - LLM 可在对话中按需查询类型定义、函数签名、接口契约

2. **动态代码分析** — `_dynamic_go_guidance()` 分析代码内容自动注入指导
   - 检测 interface → 建议创建 mock
   - 检测 error 返回 → 提醒测试错误路径
   - 检测 goroutine/channel → 建议使用 WaitGroup + 超时
   - 检测 context.Context → 提醒测试取消/超时路径
   - 检测 os 文件操作 → 建议 t.TempDir()
   - 检测 http/net → 建议 httptest.NewServer
   - 检测 io.Reader/Writer → 建议 bytes.Buffer
   - 检测 sync.Mutex → 提醒并发场景
   - 检测 reflect → 提醒覆盖不同 Kind

3. **Prompt 结构对齐 Python gpt-v2**
   - 角色设定 + 覆盖率描述 + 行标注 + 约束 + 代码摘录
   - 分支信息现在会出现在 `{missing_desc}` 中

---

## Phase 3: Production Validation & Bug Fixes (2026-02)

### 关键 Bug 修复

1. **临时测试文件命名 Bug（ROOT CAUSE of G=0）**
   - **问题**：`go_backend.py` line 178 生成的临时测试文件名为 `coverup_tmp_...605.go`，不以 `_test.go` 结尾
   - **影响**：Go 编译器忽略不以 `_test.go` 结尾的文件中的测试函数，导致所有生成的测试**从未被执行**
   - **修复**：`temp_name = f"coverup_tmp_{os.getpid()}_{task_name}_{segment.begin}_test.go"`
   - **效果**：G=0 → G=87，覆盖率 90.9% → 97.7%

2. **JSON 解析崩溃（DeepSeek 兼容性）**
   - `llm.py` `_call_function()` 中 DeepSeek 返回的 tool call 参数偶尔包含畸形 JSON
   - 添加 `try/except json.JSONDecodeError`，跳过畸形调用而非崩溃

3. **`_enforce_test_size` RuntimeError 崩溃**
   - `coverup.py` `improve_coverage()` 中添加 `except RuntimeError` 处理测试大小限制异常

4. **goimports 发现机制**
   - 新增 `GoBackend._find_goimports()` 静态方法
   - 依次搜索 `PATH`、`GOBIN`、`GOPATH/bin`、`$HOME/go/bin`
   - 替代简单的 `shutil.which("goimports")`

### SSL 传输错误抑制

- **问题**：`asyncio.run()` 结束后，litellm/httpx 残留的 SSL 连接在事件循环关闭时触发 `RuntimeError: Event loop is closed` 日志噪音
- **修复**：在 `coverup.py` 的 `main()` 中，`asyncio.run()` 之后的 `finally` 块中设置 `logging.getLogger("asyncio").setLevel(logging.CRITICAL)`
- Python 3.10 asyncio 已知问题，无害但影响用户体验

### Prompt 约束增强（`gpt_go_v1.py`）

新增 3 条约束规则，针对最常见的编译/运行时失败：

| 约束 | 解决的问题 |
|------|-----------|
| "Go forbids unused variables. Every declared variable MUST be used. Use `_` to discard." | 编译错误 "declared and not used"（占 10/14 编译失败） |
| "Do NOT assign to package-level functions (e.g. `CheckErr = ...`)" | 编译错误 "cannot assign to function" |
| "Use `{{.UnknownField}}` rather than raw `{{` for template error testing" | 运行时 panic "unexpected EOF"（4 次模板相关崩溃） |

### 最终运行结果

```
Target: src/cobra (github.com/spf13/cobra)
Model: deepseek/deepseek-coder
Results: G=87, F=66, U=1, R=0
Coverage: 90.9% → 97.7% (+6.8pp)
Cost: ~$0.23
```

**66 FAILED 分析：**
- 编译错误 14：未使用变量 10、类型不匹配 2、未知字段 2、不可赋值函数 1、未定义符号 1
- 测试断言失败 44：flag 相关 37、文档生成 10、补全命令 8、其他 6
- Panic 崩溃 4：模板引擎 unexpected EOF / undefined function

---

## Phase 1: Initial Go Support Hardening (prior)

### Backend Enhancements
- Added deterministic temp-file naming, aggressive cleanup, and gofmt/goimports post-processing.
- Captured formatter output and embedded the generated test source in the run log whenever `go test` fails.

### Prompting Improvements
- Extended prompt with `_extra_guidance` so segment-specific hints are injected into initial, retry, and missing-coverage prompts.

### Verification
- Confirmed `go test ./...` succeeds within `src/cobra`.
- CoverUp runs now surface the generated Go test content and formatter diagnostics when retries are required.
