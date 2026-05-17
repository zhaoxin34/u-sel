## Why

当前 usel 的 output 是静态文本，用户无法在选择时进行动态组合。引入模板嵌套功能后，用户可以通过选择逐步构建命令，实现类似 "echo {{poem}}" → 选择 "白日" → 输出 "echo 白日" 的交互体验。

## What Changes

- **新增模板解析引擎**：识别 `{{group}}` 占位符，按出现顺序从左到右替换
- **新增嵌套选择模式**：检测到占位符后，进入该 group 的选项列表
- **新增嵌套状态 UI**：显示当前正在解析的 group，保持用户上下文
- **新增错误处理**：group 不存在或为空时主动报错退出
- **递归支持**：替换后可继续检测新的占位符，支持多层嵌套（建议最多 3 层）

## Capabilities

### New Capabilities

- `template-resolution`: 模板解析引擎，处理 `{{group}}` 占位符的识别、替换和递归
- `nested-ui`: 嵌套状态下的 UI 显示，包含解析提示和分组选项过滤

### Modified Capabilities

- 无

## Impact

- `src/usel/app.py`: 核心状态机逻辑和 UI 渲染
- `src/usel/models.py`: 可能需要扩展数据结构（当前够用）
- `src/usel/cli.py`: 无需修改
