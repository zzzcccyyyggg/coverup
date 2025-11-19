啊，我懂你意思了——不是“用 Go 测试 Python 项目”，而是**用 Go 重写一个 CoverUp**，对 Go 项目做 LLM 驱动的自动补测，对吧。这个完全可以做，而且结构上跟原版 CoverUp 很像，只是要换成 Go 生态的一整套：`go test -cover`, `go/ast`, `go/types` 等。

我给你一个 **可以动手实现的工程方案**，按模块拆开讲，并且尽量对照 Python 版 CoverUp。

---

## 0. 整体架构（Go 版 CoverUp）

目标：

> 对一个 Go module（或某个 package）：
>
> 1. 跑一次 `go test -coverprofile` 拿覆盖率
> 2. 静态分析 AST，把“缺覆盖的函数/代码块”切成 segment
> 3. 给 LLM 一个 segment + 缺覆盖信息，要求生成 Go 测试（`*_test.go`）
> 4. 写入测试文件，重新跑 `go test`，如果编译错误 / 测试失败 / 没提升覆盖 → 和 LLM 继续对话
> 5. 并行处理多个 segment，有 checkpoint，能恢复

可以按以下包划分：

```text
cmd/coverup-go/       # CLI 主程序
internal/coverage/    # go test -cover 的封装和解析
internal/segment/     # AST + 覆盖率 → CodeSegment 切片
internal/prompt/      # prompt 生成 & 提示风格
internal/llm/         # LLM 客户端封装，含 get_info tool
internal/testrun/     # 写测试文件，调用 go test，解析错误/覆盖
internal/checkpoint/  # 状态持久化
```

---

## 1. 覆盖率测量模块（internal/coverage）

### 1.1 调用 go test -coverprofile

* 用 Go 自己调 `go test`，例如：

```go
func RunCoverage(pkgPattern string, extraArgs []string) (profilePath string, err error) {
    // profile 写到一个临时文件
    tmp := filepath.Join(os.TempDir(), "coverup-go-profile.out")

    args := []string{"test", "-covermode=count", "-coverprofile=" + tmp}
    args = append(args, extraArgs...)
    args = append(args, pkgPattern) // e.g. "./..."

    cmd := exec.Command("go", args...)
    cmd.Stdout = os.Stdout // 或缓冲并记录
    cmd.Stderr = os.Stderr
    err = cmd.Run()
    if err != nil {
        return "", err
    }
    return tmp, nil
}
```

### 1.2 解析 coverprofile → 每文件的覆盖信息

* `go tool cover` 的 profile 格式类似：

  ```
  mode: count
  path/to/file.go:line0.col0,line1.col1 num-stmts count
  ```
* 可用 `golang.org/x/tools/cover` 包里的解析器（`ParseProfiles`），得到 `[]*cover.Profile`：

  * 每个 profile 包含一系列 `Block`：行号范围 + 是否被执行 + 执行计数。

你可以构造一个内部结构类似 Python 版的：

```go
type FileCoverage struct {
    FilePath       string
    Blocks         []BlockCoverage
    MissingLines   map[int]struct{}
    ExecutedLines  map[int]struct{}
    // 可选: MissingBranches (Go 没原生 branch coverage，只能 approximate)
}

type BlockCoverage struct {
    StartLine int
    EndLine   int
    Count     int
}
```

然后把每个 block 的行区间展开成行号集合，统计出：

* `MissingLines`: 所有 `Count == 0` 的 block 覆盖到的行
* `ExecutedLines`: 所有 `Count > 0` 的 block 覆盖到的行

> Go 没原生“分支覆盖”，你可以先只做行/块覆盖；如果想搞 branch，可以在 AST 级别识别 `if` / `switch` 条件，维护一个“条件被执行但某分支从未 hit”的标记。

---

## 2. Segment 切片模块（internal/segment）

这个就是 Go 版的 `CodeSegment` 和 `get_missing_coverage`。

### 2.1 使用 go/parser / go/ast 解析源文件

```go
fset := token.NewFileSet()
fileAst, err := parser.ParseFile(fset, filePath, nil, parser.ParseComments)
```

### 2.2 定义 Go 版 CodeSegment

```go
type CodeSegment struct {
    FilePath  string
    FuncName  string        // 函数/方法名字，如 "Do", "(*Server).ServeHTTP"
    BeginLine int           // segment 起始行
    EndLine   int           // segment 终止行（开区间）
    LinesOfInterest map[int]struct{}
    MissingLines    map[int]struct{}
    ExecutedLines   map[int]struct{}
    // 缺分支可选
    ContextRanges   [][2]int    // 上下文行（如外层 type/方法）
    Imports         []string    // 为 prompt 提供必要 import
}
```

### 2.3 如何从覆盖信息切 segment

思路跟 Python 版几乎一模一样：

1. 对每个文件 `FileCoverage`，拿 `MissingLines` 作为 `linesOfInterest`。
2. 对每个 `line`：

   * 如果已经被某个 segment 覆盖 → 跳过；
   * 用 AST 查找“包含该行的函数/方法或 type 声明”。

伪代码：

```go
func FindEnclosing(f *ast.File, fset *token.FileSet, line int) (node ast.Node, begin, end int) {
    var result ast.Node
    var b, e int

    ast.Inspect(f, func(n ast.Node) bool {
        if n == nil {
            return true
        }
        // 限定在 FuncDecl, MethodDecl, TypeSpec (struct) 等
        switch x := n.(type) {
        case *ast.FuncDecl:
            pos := fset.Position(x.Pos())
            endPos := fset.Position(x.End())
            if pos.Line <= line && line <= endPos.Line {
                result = n
                b = pos.Line
                e = endPos.Line + 1
                // 不 return false，因为可能有更内层（例如匿名函数），你可以选择策略
            }
        case *ast.TypeSpec:
            // 对 struct type，如果你想支持“大 struct 里分拆 method”，可以作为 context
        }
        return true
    })
    return result, b, e
}
```

3. 如果 `end-begin` 太大（超过 `lineLimit`，比如 80 行），参考 CoverUp 的“class 过大往里缩”逻辑：

   * 在 Go 里可类似：如果是大文件或大 type，则继续在 node 内查找更内层的函数/method literal；
   * or 简单版：只以函数/方法为粒度，忽略太大的 `type` 段。

4. 每个 `(begin,end)` 只创建一个 `CodeSegment`，并记录：

   * 该段内的 `missingLines`/`executedLines`;
   * `LinesOfInterest` 为 `MissingLines ∪ ???`；
   * `ContextRanges` 可以用来输出一些外层的 type/包级变量定义。

### 2.4 导入信息（Imports）

类似 Python 版 `get_global_imports`，你可以：

* 遍历 `fileAst.Imports`；
* 简单策略：把整个 `import (...)` 块原样放进 excerpt；
* 或做一点筛选：只保留真正用到的 import（通过 type 信息或 `ast.Ident` 用法分析）。

---

## 3. Prompt 构造（internal/prompt）

对 Go 来说，你的 prompt 可以长这样（类比论文里的 Fig.3/4）：

> 你是一个资深的 Go 测试驱动开发工程师。
> 下面是 Go 包中的一段代码片段，来自文件 `pkg/foo/bar.go`，函数 `DoSomething`。
> 当前测试覆盖率分析显示，以下行没有被覆盖：
> `lines: [23, 24, 27]`
> 请为这个函数编写一个 Go 单元测试，放在 `*_test.go` 文件中。
> 要求：
>
> * 使用 `testing` 包标准写法
> * 不要使用外部依赖
> * 尽量覆盖上述行
> * 只输出完整的 Go 代码，放在 `go ` 代码块中
> * 测试函数以 `Test` 开头
>
> ```go
> // 这里是 imports + context（type 定义） + segment 代码
> ```

你可以定义一个 `Prompter` 接口，与 Python 版类似：

```go
type Prompter interface {
    InitialPrompt(seg segment.CodeSegment) []LLMMessage
    ErrorPrompt(seg segment.CodeSegment, errorOutput string) []LLMMessage
    MissingCoveragePrompt(seg segment.CodeSegment, stillMissing []int) []LLMMessage
}
```

---

## 4. LLM 客户端 & get_info 工具（internal/llm）

### 4.1 LLM 封装

和 Python 版一样，你写一个 `Chatter`：

```go
type Chatter struct {
    Client    OpenAIClient // 或通用接口
    Model     string
    // rate limit, backoff, logging...
}

func (c *Chatter) Chat(messages []LLMMessage, tools []ToolDef, ctx any) (LLMResponse, error) {
    // 调用 OpenAI / 其他 LLM
}
```

### 4.2 `get_info` tool 的 Go 版

功能同样是：给 LLM 提供“某个标识符的定义摘要”，避免它乱猜。

* 利用 `go/packages` + `go/ast` + `go/types`：

  1. 从当前文件的包加载整个包：`packages.Load(&packages.Config{Mode: packages.LoadAllSyntax}, "your/module/pkg/...")`
  2. 用 `types.Info` 确定标识符 → 其 `types.Object`（函数、变量、type 等）。
  3. 定位到定义对应的 `ast.Node`，用类似 CoverUp 的 `_summarize` 方法：

     * 对函数体，仅保留签名和关键参数/返回值，主体替换为 `{ ... }`；
     * 对 struct，仅保留字段列表，把 field tag/body简化。
  4. 用 `go/printer.Fprint` 或 `go/format.Source` 输出代码片段。

返回给 LLM 的格式可以是：

````text
in pkg/path/file.go:
```go
type A struct {
    X int
    Y string
    ...
}

func (a *A) DoSomething(arg int) error {
    ...
}
````

````

这样与论文 Fig.9 非常类似，只是语言变成 Go。

---

## 5. 测试生成与执行（internal/testrun）

### 5.1 从 LLM 响应中抽取 Go 代码

- 使用正则类似：

```go
re := regexp.MustCompile("```go\\s*(?s)(.*?)```")
m := re.FindStringSubmatch(resp)
if len(m) < 2 { ... } 
code := m[1]
````

### 5.2 写入测试文件

* 约定：所有新测试都写进 `coverup_xxx_test.go`。
* `args.testsDir` 相当于 Go 包目录，比如 `./pkg/foo`。

```go
func NewTestFile(dir string, seq int) (string, error) {
    name := fmt.Sprintf("coverup_%03d_test.go", seq)
    path := filepath.Join(dir, name)
    if _, err := os.Stat(path); err == nil {
        return "", os.ErrExist
    }
    return path, os.WriteFile(path, []byte(code), 0644)
}
```

### 5.3 运行 go test 验证

* 每次新增一个测试后，执行：

```go
cmd := exec.Command("go", "test", "./pkg/foo", "-run", "TestCoverup.*", "-count=1")
var out bytes.Buffer
cmd.Stdout = &out
cmd.Stderr = &out
err := cmd.Run()
if err != nil {
    // parse out.String()，传给 ErrorPrompt 让 LLM 修测试
}
```

* 如果通过，再跑一次 `go test -coverprofile`，比较覆盖：

```go
newProfile, _ := RunCoverage("./pkg/foo", nil)
newCov := ParseCoverage(newProfile)
// 对比 seg 对应文件的 MissingLines 是否减少
```

如果没减少：（相当于 U= useless）：

* 调 `MissingCoveragePrompt`，告诉 LLM “lines X,Y 仍未覆盖”，继续对话。

---

## 6. 并发 & 速率控制（goroutines + sem）

### 6.1 Segment 并发处理

* 跟 Python 的 asyncio 类似，用 goroutine + `sync.WaitGroup`：

```go
sem := make(chan struct{}, maxConcurrency)

for _, seg := range segments {
    if state.IsDone(seg) { continue }

    wg.Add(1)
    go func(seg CodeSegment) {
        defer wg.Done()
        sem <- struct{}{}
        defer func() { <-sem }()

        err := ImproveCoverageForSegment(seg)
        if err == nil {
            state.MarkDone(seg)
        }
        state.SaveCheckpoint(...)
    }(seg)
}

wg.Wait()
```

### 6.2 速率限制

* 用 `time.Ticker` + channel 或 `golang.org/x/time/rate`，在 `Chatter.Chat` 前做限流。
* 遇到 429 / 超时 → 指数回退重试（与 Python CoverUp 的 `max_backoff` 一致）。

---

## 7. 状态 & checkpoint（internal/checkpoint）

定义一个与 Python `State` 类等价的结构：

```go
type State struct {
    Done      map[string][][2]int  // file → list of (begin,end)
    CostUSD   float64
    Counters  map[string]int       // G/F/U/R
    Coverage  map[string]FileCoverage
    FinalCov  *map[string]FileCoverage
}
```

* 用 JSON 存到 `checkpoint.json`：

  * 启动时先尝试读；
  * 若存在，直接用旧 coverage，不再重新测；
  * 每处理完一个 segment 就写一次。

---

## 8. 对 Go 特性的额外考虑

* **测试命名 & 多文件**：

  * Go 单测是 per-package 的，所以你给某个文件写测试，实际要跑整个包；
  * 这意味着“state pollution” 也可能存在（global 变量、init() 等），但 Go 没 fork 测试那种：

    * 你可以在“整包测试失败”时用反复 `-run TestX` 二分法找出导致失败的测试，重命名/跳过；
    * 或简单方案：失败就把这个 `coverup_xxx_test.go` 重命名为 `disabled_coverup_xxx_test.go`，类似原 CoverUp。

* **Go fuzz**：

  * 之后你还可以把 LLM 生成的普通测试函数，扩展成 fuzz target（`FuzzXxx(f *testing.F)`），再用 `go test -fuzz` 做二段式扩展，这个可以是论文里一个 nice extension。

---

## 9. 一个简短的落地路线图

你可以按这个顺序来做 MVP：

1. **只做简单版：**

   * 只支持行覆盖；
   * 只对一个 package（比如 `./mypkg`）；
   * 不搞 get_info 工具，prompt 里只放 segment excerpt。

2. 打通闭环：

   * `go test -coverprofile` → 解析 profile → 找到 1~2 个 MissingLines 密集的函数；
   * 对这几个函数构造 prompt，手动调 LLM（可以先写假 Client）；
   * 把返回的 Go 测试放到 `coverup_xxx_test.go`，跑 go test & cover，看 coverage 变化。

3. 然后再迭代：

   * 补齐 get_info；
   * 做并发和 checkpoint；
   * 做 error follow-up / missing coverage follow-up；
   * 最后再考虑 fuzz 集成。

---

如果你愿意，下一步我可以帮你：

* **直接设计一个包结构 & 最小可运行 main.go**，
* 再写一个具体示例：比如对 `net/http` 里某个简单 handler 做一轮完整 CoverUp-Go 流程（包括 sample prompt 和预期测试代码）。
