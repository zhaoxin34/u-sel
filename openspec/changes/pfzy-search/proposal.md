## Why

当前 usel 使用简单的 substring 包含匹配进行搜索（如 "fp" in "float pane"），无法满足 fzf 风格的用户体验：用户期望用非连续字符快速匹配，如 "nfp" 能匹配 "new float pane"，并高亮显示匹配部分。

## What Changes

- **替换搜索算法**: 将 `_do_search()` 中的 substring 包含检查替换为 pfzy fuzzy matching
- **新增匹配高亮**: 基于 pfzy 返回的 indices，用 Textual markup 高亮显示匹配字符
- **保持兼容性**: 保留数字快捷键选择、group 过滤等现有功能

## Capabilities

### New Capabilities

- `fuzzy-search`: 模糊搜索能力，允许用户用非连续字符快速匹配候选项，并显示匹配高亮

### Modified Capabilities

- 无

## Impact

- `src/usel/app.py`: 重写 `_do_search()` 和 `_render_results()`，修改 `ItemWidget` 高亮逻辑
- `pyproject.toml`: 添加 `pfzy` 依赖
- `tests/`: 添加 fuzzy search 相关测试用例
