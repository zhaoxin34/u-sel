## ADDED Requirements

### Requirement: 占位符识别

系统 SHALL 能够从 output 字符串中识别 `{{group_name}}` 格式的占位符，其中 `group_name` 必须是连续的字母、数字、下划线（`\w+`）。

#### Scenario: 识别单个占位符

- **WHEN** output 为 `echo "{{poem}}"`
- **THEN** 系统识别出占位符 `poem`

#### Scenario: 识别多个占位符

- **WHEN** output 为 `echo "{{poem}}" and "{{greeting}}"`
- **THEN** 系统识别出第一个占位符 `poem`（按从左到右顺序）

#### Scenario: 不匹配非占位符文本

- **WHEN** output 为 `echo "{{not a valid group}}" or "just text {{a}"
- **THEN** 系统识别出 `a`（第二个 `{{a}` 是有效占位符）

#### Scenario: 无占位符时返回 None

- **WHEN** output 为 `echo "hello"`
- **THEN** 系统返回 None（无占位符）

### Requirement: 占位符替换

系统 SHALL 能够用用户选择的 value 替换 output 中第一个匹配的 `{{group_name}}` 占位符，且只替换第一个，不影响后续占位符。

#### Scenario: 替换单个占位符

- **WHEN** output 为 `echo "{{poem}}"`，用户选择 value 为 `白日`
- **THEN** 结果为 `echo "白日"`

#### Scenario: 替换后保留后续占位符

- **WHEN** output 为 `echo "{{poem}}" and "{{greeting}}"`，`poem` 替换为 `白日`
- **THEN** 结果为 `echo "白日" and "{{greeting}}"`（`{{greeting}}` 保留）

#### Scenario: 替换多个同名占位符（只替换第一个）

- **WHEN** output 为 `say "{{name}}" to {{name}}`，选择 name=Alice
- **THEN** 结果为 `say "Alice" to {{name}}`（只有第一个被替换）

### Requirement: 嵌套深度限制

系统 SHALL 限制模板递归深度最多为 3 层，超过时主动报错退出。

#### Scenario: 达到第 3 层时正常完成

- **WHEN** 用户进行 3 次嵌套选择
- **THEN** 系统正常输出最终结果

#### Scenario: 第 4 层时报错

- **WHEN** 用户尝试进行第 4 次嵌套选择
- **THEN** 系统输出错误消息 "嵌套层数超过限制（3层）" 并退出

### Requirement: Group 查询与验证

系统 SHALL 能够根据 group_name 查询对应的选项列表，并在 group 不存在或为空时主动报错退出。

#### Scenario: Group 存在且有选项

- **WHEN** 需要解析 `{{poem}}`，且 group=poem 下存在选项
- **THEN** 系统返回 poem 组的所有选项供用户选择

#### Scenario: Group 不存在

- **WHEN** 需要解析 `{{music}}`，但配置中不存在 group=music
- **THEN** 系统输出错误消息 "Group 'music' 不存在或为空" 并退出

#### Scenario: Group 存在但无选项

- **WHEN** 需要解析 `{{empty}}`，但 group=empty 下没有选项
- **THEN** 系统输出错误消息 "Group 'empty' 不存在或为空" 并退出

### Requirement: 递归循环解析

系统 SHALL 在每次替换后自动检查 output 是否仍有占位符，如有则继续递归解析，直到 output 中无占位符为止。

#### Scenario: 无需递归的简单选择

- **WHEN** 用户选择 output 为 `echo "hello"`（无占位符）
- **THEN** 系统直接输出 `echo "hello"`

#### Scenario: 需要 2 层递归

- **WHEN** 选择 output 为 `echo "{{poem}}"`
- **THEN** 用户选择 "白日" 后，系统继续检查，发现无占位符，输出最终结果

#### Scenario: 需要 3 层递归

- **WHEN** 选择 output 为 `echo "{{a}}"`
- **THEN** 解析 a 后得到 `say "{{b}}"` → 解析 b 后得到 `hi` → 输出 `echo "hi"`
