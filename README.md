# 背景

我用zellij作为我的多路复用器，同时用PI作为Coding Agent，我发现PI有个很好用的package，叫btw，应该这么说，这个功能很好，但是实现都很差劲，差在哪，差在交互，原因也很简单，这些package的开发者在这方面并没有投入太大精力，但是他们的思想很好。

# 怎么办

zellij不就是最好的交互终端吗，btw就是要弹出一个窗口，然后问个问题，然后结束，他的模型是什么，弹框 -> 输入提示词 --> 关闭窗口，目标是不打扰当前会话，这不就是zellij最擅长的吗。

## 解法

快捷键 -> 弹框`[zellij float or stack and close on exit]` -> 执行一个python写的TUI窗口 -> search and select -> 输出一个命令 -> zellij pane 执行这个命令，而本项目只需要做search and select 并输出这个命令的功能。

## 实现方案细节

### 配置文件

程序启动加载一个yml，配置着标题、分组、描述、输出的列表，随着输入不断过滤候选项，称它为 sels.yml,上下可以选择候选项，回车选中，把命令输出。

sels.yml 从 ~/.config/u-sel/sels.yml 中获取，示例如下

```yaml
- title: pi -c
  group: pi
  description: 启动PI，继续上次会话
  output: pi -c
- title: pi -r
  group: pi
  description: 启动PI，选择一个会话
  output: pi -r
```

### 占位符语法

output 支持占位符语法 `{{意图[:提示语][|默认值]}}`，用于动态内容替换：

| 意图 | 说明          | 示例                                |
| ---- | ------------- | ----------------------------------- |
| `g`  | 从 group 选择 | `{{g\|zellij}}` 从 zellij group 选  |
| `i`  | 手动输入      | `{{i:请输入端口\|8080}}` 弹出输入框 |

#### g 模式 - Group 选择

```yaml
- title: zellij - new float pane
  group: zellij
  output: zellij action new-pane -c -- bash -c "{{g|pi}}"
```

用户选择后，占位符被替换为选中的 output。

#### i 模式 - 手动输入

```yaml
- title: 快速输入端口
  group: input
  output: echo "Port: {{i:请输入端口|8080}}"
```

- 提示语 `请输入端口` 显示在输入框上方
- 默认值 `8080` 预填充在输入框中
- 用户输入后（trim 处理），回车确认
- 空输入会报错退出

#### 嵌套多个占位符

output 可以包含多个占位符，按顺序解析：

```yaml
- title: docker run
  group: docker
  output: docker run -p {{i:端口号|8080}} -v {{g|volumes}}:/data
```

### 使用技术栈

### 发布

发布成 cli：usel

### 应用方法

zellij action new-pane --floating --width 60% --height 60% --x 20% --y %20 -c -- bash -c "$(usel)"
