# 背景

我用zellij作为我的多路复用器，同时用PI作为Coding Agent，我发现PI有个很好用的package，叫btw，应该这么说，这个功能很好，但是实现都很差劲，差在哪，差在交互，原因也很简单，这些package的开发者在这方面并没有投入太大精力，但是他们的思想很好。

# 怎么办

zellij不就是最好的交互终端吗，btw就是要弹出一个窗口，然后问个问题，然后结束，他的模型是什么，弹框 -> 输入提示词 --> 关闭窗口，目标是不打扰当前会话，这不就是zellij最擅长的吗。

## 解法

快捷键 -> 弹框`[zellij float or stack and close on exit]` -> 执行一个python写的TUI窗口 -> search and select -> 输出一个命令 -> zellij pane 执行这个命令，而本项目只需要做search and select 并输出这个命令的功能。

## 实现方案细节

### 配置文件

程序启动加载一个yml，配置着标题、分组、描述、输出的列表，随着输入不断过滤候选项，称它为sels.yml,上下可以选择候选项，回车选中，把命令输出。

sels.yml 从~/.config/u-sel/sels.yml中获取，示例如下

```
- title: pi -c
  group: pi
  description: 启动PI，继续上次会话
  output: pi -c
- title: pi -r
  group: pi
  description: 启动PI，选择一个会话
  output: pi -r
- title: pi --no-session
  group: pi
  description: 启动PI，不持久化会话
  output: pi --no-session

```

### 使用技术栈

### 发布

发布成cli：usel

### 应用方法

zellij action new-pane --floating --width 60% --height 60% --x 20% --y %20 -c -- bash -c "$(usel)"

## 试着勇敢一点

之前的实现方法很好，但是还是可以更进一步。

我是这么想的，output是不是可以嵌套，比如

```
- title: echo
  group: echo something
  output: echo "{{poem}}"
- title: 白日
  group: poem
  output: 白日依山尽
```

当使用usel进入界面后，我可以先选择echo，按下回车，此时应该输出 echo "{{poem}}", 代码发现里面包含`{{poem}}`, 其中，poem就是个group，则应该再生成一下候选项，然后，最终会输出 echo "白日依山尽", 假设 白日 对应的output还是带有 `{{}}`的，比如变成 echo "白日依山尽 {{poem}}", 则再生成一次，直至`{{}}`不再存在。
