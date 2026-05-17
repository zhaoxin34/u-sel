## 1. 模板解析核心

- [x] 1.1 添加 `_current_output` 状态变量到 USelApp
- [x] 1.2 添加 `_mode` 状态变量（normal/resolving）
- [x] 1.3 添加 `_current_group` 状态变量
- [x] 1.4 添加 `_depth` 计数器（最大 3）
- [x] 1.5 实现 `extract_group(output)` 函数，使用正则 `\{\{(\w+)\}\}`
- [x] 1.6 实现 `replace_placeholder(output, group, value)` 函数
- [x] 1.7 实现 `_check_and_continue()` 递归检查逻辑

## 2. 嵌套状态处理

- [x] 2.1 修改 `_confirm_selection()` 支持 normal 模式下设置 `_current_output`
- [x] 2.2 添加 group 不存在/为空的错误检测
- [x] 2.3 添加嵌套深度超限检测（> 3 层报错）
- [x] 2.4 在 resolving 模式下用选中值替换占位符

## 3. UI 嵌套模式显示

- [x] 3.1 修改 `_update_results()` 支持传入过滤的 selections
- [x] 3.2 在 resolving 模式下添加顶部提示 `🔄 正在解析 {{group}}...`
- [x] 3.3 在 resolving 模式下只显示目标 group 的选项
- [x] 3.4 在 normal 模式下显示所有选项（原有行为）

## 4. 配置与测试数据

- [x] 4.1 更新 `~/.config/u-sel/sels.yml` 添加嵌套测试数据
- [x] 4.2 添加 template 组和 nested 组用于测试
- [x] 4.3 添加 3 层嵌套测试用例

## 5. 错误处理

- [x] 5.1 实现 `sys.exit()` 或 raise 异常退出
- [x] 5.2 显示友好的错误消息（中文）
- [x] 5.3 确保 q 键在嵌套模式下也能正常退出

## 6. 测试与验证

- [ ] 6.1 测试单层嵌套（echo → {{poem}} → 白日）
- [ ] 6.2 测试多层嵌套（3 层）
- [ ] 6.3 测试 group 不存在报错
- [ ] 6.4 测试嵌套超过 3 层报错
- [ ] 6.5 测试多个占位符按顺序替换
