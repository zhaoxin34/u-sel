## Why

当前占位符 `{{group_name}}` 只能从预设选项中选择，无法支持用户手动输入自定义内容。例如用户想输入一个自定义的端口号、文件名等，只能通过创建新的 group 条目来实现，缺乏灵活性。

## What Changes

- **新占位符语法**: `{{意图[:提示语][|默认值]}}`
  - `g` 意图：group 选择模式，显示对应 group 的选项列表
  - `i` 意图：input 模式，弹出输入框提示用户手动输入
- **提示语支持**：g 和 i 模式都支持自定义提示语，显示在选项列表或输入框上方
- **默认值支持**：input 模式的输入框可预填充默认值
- **BREAKING**: 旧语法 `{{group_name}}` 需迁移到 `{{g|group_name}}`

## Capabilities

### New Capabilities

- placeholder-v2: 占位符语法增强，支持意图-driven 的选择和输入模式

### Modified Capabilities

- 占位符: 原有 `{{group_name}}` 语法扩展为 `{{意图[:提示语][|默认值]}}`

## Impact

- `src/usel/app.py`: 占位符解析逻辑、g/i 模式 UI 实现
- `~/.config/u-sel/sels.yml`: 配置迁移（旧语法 → 新语法）
