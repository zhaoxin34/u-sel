## 1. 解析器重构

- [x] 1.1 更新正则表达式支持新语法 `{{意图[:提示语][|默认值]}}`
- [x] 1.2 创建 `Placeholder` dataclass 存储解析结果（intent, prompt, default, group_name）
- [x] 1.3 实现 `parse_placeholder()` 函数返回 Placeholder 对象
- [x] 1.4 添加旧语法检测，当检测到 `{{word}}` 且 word 非 g/i 时报错提示迁移

## 2. 状态机实现

- [x] 2.1 添加状态 `_mode: Literal["searching", "resolving_g", "resolving_i"]`
- [x] 2.2 添加 `_current_placeholder: Placeholder | None` 存储当前解析结果
- [x] 2.3 实现 `_enter_resolve_mode()` 根据意图切换状态
- [x] 2.4 更新 `_check_and_continue()` 使用新的解析逻辑

## 3. g 模式 UI

- [x] 3.1 重用 `_mode == "resolving"` 时显示 group 选项列表
- [x] 3.2 在结果区域上方显示提示语（自定义或默认"请选择"）
- [x] 3.3 选择后调用 `replace_placeholder()` 替换

## 4. i 模式 UI

- [x] 4.1 检测到 `i` 意图时清空选项列表
- [x] 4.2 在输入框区域显示提示语
- [x] 4.3 下方显示预填充默认值的输入框
- [x] 4.4 回车时获取输入内容，trim 后验证非空
- [x] 4.5 空输入时报错退出

## 5. 替换与继续

- [x] 5.1 实现 `replace_placeholder()` 函数处理 g/i 两种模式
- [x] 5.2 替换后继续检查剩余字符串中的下一个占位符
- [x] 5.3 保持最大嵌套深度检查（MAX_DEPTH=3）

## 6. 配置迁移

- [x] 6.1 更新 `~/.config/u-sel/sels.yml` 示例配置
- [x] 6.2 添加新语法使用示例（g 模式和 i 模式）
- [x] 6.3 更新 README 文档说明新语法

## 7. 测试

- [x] 7.1 编写正则表达式解析测试
- [ ] 7.2 编写 g 模式交互测试
- [ ] 7.3 编写 i 模式交互测试
- [ ] 7.4 编写错误处理测试（旧语法、group 不存在、空输入）
