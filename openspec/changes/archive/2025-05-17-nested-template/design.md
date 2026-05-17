## Context

当前 usel 的数据结构是扁平的 `Selection` 列表，每个 item 有 `title`、`group`、`output`。用户选择一个 item 后直接输出其 `output`。

为了支持模板嵌套，需要：

1. 解析 `output` 中的 `{{group_name}}` 占位符
2. 检测到占位符时，切换到"嵌套选择模式"，只显示目标 group 的选项
3. 用户选择后，用选中的 `output` 替换占位符
4. 递归检查替换后的 output，直到无占位符为止

## Goals / Non-Goals

**Goals:**

- 支持 `{{group_name}}` 语法解析
- 按从左到右顺序处理多个占位符
- 嵌套模式下显示特殊提示 UI
- 递归深度最多 3 层
- group 不存在或为空时主动报错退出

**Non-Goals:**

- 不支持嵌套 group 名（如 `{{outer{{inner}}}}`）
- 不支持变量或条件逻辑
- 不修改配置文件的 YAML 结构（保持向后兼容）
- 不支持在 group 选择时再嵌套（3 层足够）

## Decisions

### 1. 状态机设计

```python
class USelApp(App):
    # 新增状态
    _mode: Literal["normal", "resolving"] = "normal"
    _current_output: str = ""
    _current_group: str | None = None
    _depth: int = 0
```

- `normal` 模式：显示所有选项，用户选择后进入下一状态
- `resolving` 模式：显示特定 group 的选项，替换后回退到 normal 检查

### 2. 占位符解析

```python
import re

PLACEHOLDER_PATTERN = re.compile(r'\{\{(\w+)\}\}')

def extract_group(output: str) -> str | None:
    match = PLACEHOLDER_PATTERN.search(output)
    return match.group(1) if match else None

def replace_placeholder(output: str, group: str, value: str) -> str:
    return output.replace(f'{{{{{group}}}}}', value, 1)  # 只替换第一个
```

### 3. 递归循环

```
def resolve_loop():
    while True:
        group = extract_group(_current_output)
        if not group:
            return _current_output  # 最终输出

        if _depth >= 3:
            raise ExitWithError("嵌套层数超过限制（3层）")

        options = get_group_options(group)
        if not options:
            raise ExitWithError(f"Group '{group}' 不存在或为空")

        _mode = "resolving"
        _current_group = group
        _depth += 1
        # UI 显示 options，用户选择后返回
```

### 4. UI 渲染

```python
# 正常模式
content = f"[dim #888888]{num:>3}. [/dim #888888][#C4E88D]{title}[/#C4E88D]  [dim #FE747E]`{output}`[/dim #FE747E]  [dim #4FD6BE]({group})[/dim #4FD6BE]"

# 嵌套模式
hint = f"[yellow]🔄 正在解析 {{{{{group}}}}}...[/yellow]"
# 只显示 group 下的选项，并显示返回路径
```

### 5. 选择确认逻辑

```python
def on_confirm():
    if _mode == "normal":
        _current_output = selected.output
    else:  # resolving
        _current_output = replace_placeholder(_current_output, _current_group, selected.output)

    # 立即检查是否还有占位符，递归处理
    _check_and_continue()
```

## Risks / Trade-offs

| Risk                             | Mitigation                                                           |
| -------------------------------- | -------------------------------------------------------------------- |
| 用户输入包含 `{{` 但不是占位符   | 占位符必须匹配 `\{\{(\w+)\}\}` 格式，空格/特殊字符会被识别为普通文本 |
| 循环依赖（a → {{b}}, b → {{a}}） | 限制 3 层递归深度，超出则报错退出                                    |
| group 名称冲突                   | 优先匹配最近添加的占位符，同名 group 使用同一配置                    |
| 输出中有多个同名占位符           | `replace(..., 1)` 只替换第一个，按从左到右顺序处理                   |
