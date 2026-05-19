## Context

当前 usel 使用简单的 substring 包含匹配进行搜索。用户在搜索 "new float pane" 时，只能通过完整或部分连续字符串匹配，如 "new" 或 "float"，无法使用 fzf 风格的非连续字符匹配（如 "nfp"）。

目标：引入 pfzy 库实现 fzf 风格的模糊搜索，同时高亮显示匹配字符。

## Goals / Non-Goals

**Goals:**

- 实现 fuzzy subsequence matching（"nfp" → "new float pane"）
- 高亮显示匹配字符，提供视觉反馈
- 保持现有交互（数字选择、上下导航、group 过滤）
- 保持向后兼容，不破坏现有功能

**Non-Goals:**

- 不实现多选功能
- 不实现搜索历史
- 不实现自定义评分算法（使用 pfzy 内置）
- 不改变占位符语法（{{g|...}}, {{i:...}}）

## Decisions

### 1. 选择 pfzy 作为搜索库

**决策**: 使用 `pfzy` 库而非其他方案

| 方案              | 优点                             | 缺点                         |
| ----------------- | -------------------------------- | ---------------------------- |
| fuzzyfinder       | 纯 Python，无依赖                | 无 indices 返回，需自行实现  |
| thefuzz/rapidfuzz | 流行，兼容性好                   | 无 indices，返回分数而非位置 |
| **pfzy**          | 返回 indices，fzf 算法，高亮友好 | 需额外安装                   |
| 自己实现          | 完全控制                         | 工作量大，容易出错           |

**结论**: pfzy 的 `fuzzy_match()` 返回 `(value, indices)`，完美满足高亮需求。

### 2. 高亮实现方式

**决策**: 使用 Textual markup 而非 ANSI codes

```python
# indices = [0, 4, 10] (匹配位置)
# "new float pane" → "[n]ew [f]loat [p]ane"

def build_highlighted_markup(text: str, indices: list[int]) -> str:
    """基于匹配 indices 构建带高亮的 markup"""
    ...
    return f"[#C4E88D]{matched_chars}[/#C4E88D]"
```

Textual 的 `Static` widget 支持 `markup=True`，可以直接渲染带颜色的文本。

### 3. 搜索范围

**决策**: 同时搜索 title、output、group 三个字段

当前实现已经搜索这三个字段，保持一致。但 fuzzy 匹配需要评分机制。

方案：

- 对每个候选项，分别计算 title/output/group 的匹配分数
- 选择最高分作为最终排序依据

### 4. 数字快捷键兼容性

**决策**: 保留数字快速选择功能

当输入全是数字时（e.g., "1", "12"），直接作为索引选择，不走 fuzzy 匹配。这与 fzf 行为一致。

### 5. 空查询处理

**决策**: 空查询显示所有选项，按 group 字母序排列

与现有行为一致，便于用户浏览。

## Risks / Trade-offs

| Risk                                  | Mitigation                                                 |
| ------------------------------------- | ---------------------------------------------------------- |
| pfzy 异步 API 与 Textual 事件循环冲突 | 使用同步 API `fzy_scorer()` 逐一匹配，而非 `fuzzy_match()` |
| 性能问题（大量候选项）                | 考虑批量处理或缓存，但初始实现保持简单                     |
| 高亮字符可能与现有样式冲突            | 定义专用 CSS 类 `.matched-char` 隔离样式                   |

## Migration Plan

1. 添加 `pfzy` 依赖到 `pyproject.toml`
2. 实现 `fuzzy_search()` 函数处理匹配和高亮
3. 修改 `ItemWidget` 支持动态高亮
4. 重写 `_do_search()` 替换现有 substring 匹配
5. 添加测试用例
6. 验证向后兼容性

**回滚策略**: 如有问题，可通过 `uv pip uninstall pfzy` 快速移除，并通过 git 回滚代码。

## Open Questions

1. 是否需要大小写敏感选项？
2. 如何处理搜索结果为空的情况？显示 "No matches" 或保持显示全部？
3. 高亮颜色是否需要可配置？
