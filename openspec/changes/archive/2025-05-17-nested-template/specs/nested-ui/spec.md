## ADDED Requirements

### Requirement: 嵌套状态提示

系统 SHALL 在进入嵌套选择模式时，在列表顶部显示当前正在解析的 group 提示，格式为 `🔄 正在解析 {{group_name}}...`。

#### Scenario: 显示嵌套状态

- **WHEN** 用户选择触发 `{{poem}}` 解析
- **THEN** UI 在选项列表顶部显示 `🔄 正在解析 {{poem}}...`

#### Scenario: 多层嵌套时显示当前层

- **WHEN** 用户处于第 2 层嵌套（正在解析 `{{b}}`，已解析了 `{{a}}`）
- **THEN** UI 显示 `🔄 正在解析 {{b}}...`

### Requirement: 嵌套模式选项过滤

系统 SHALL 在嵌套选择模式下，只显示目标 group 的选项，隐藏其他 group 的选项。

#### Scenario: 正常模式显示全部选项

- **WHEN** 系统处于 normal 模式
- **THEN** UI 显示所有可选项目

#### Scenario: 嵌套模式只显示目标 group

- **WHEN** 用户选择后触发 `{{poem}}`
- **THEN** UI 只显示 group=poem 下的选项

### Requirement: 嵌套模式下的选择高亮

系统 SHALL 在嵌套模式下保持原有的选择高亮样式（背景色变化）。

#### Scenario: 嵌套模式下键盘上下选择

- **WHEN** 用户在嵌套模式下按 up/down 键
- **THEN** 当前选中项高亮显示，向上/向下移动

### Requirement: 嵌套模式下的退出

系统 SHALL 在嵌套模式下，当用户按 q 键时，输出错误消息并退出。

#### Scenario: 嵌套模式下按 q 退出

- **WHEN** 用户在嵌套选择过程中按 q
- **THEN** 系统输出错误消息 "用户取消" 并退出程序

### Requirement: 正常模式下的交互

系统 SHALL 在正常模式下保持原有交互：

- up/down 选择
- enter 确认
- q 退出

#### Scenario: 正常模式下完整选择流程

- **WHEN** 用户在正常模式下选择选项并按 enter
- **THEN** 系统进入嵌套检查逻辑（检查是否有占位符）
