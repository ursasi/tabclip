<p align="center">
  <img src="docs/banner.svg" alt="TabClip — Copy every tab you picked, in one right-click." width="880">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/Manifest-V3-6366F1.svg" alt="Manifest V3">
  <img src="https://img.shields.io/badge/Chrome-150%2B-4285F4.svg?logo=googlechrome&logoColor=white" alt="Chrome 150+">
  <img src="https://img.shields.io/badge/dependencies-0-22C55E.svg" alt="Zero dependencies">
</p>

<h1 align="center">TabClip</h1>

<p align="center"><b>Copy every tab you picked — in one right-click.</b><br>多选标签页 → 右键 → 复制这些标签页的 URL。</p>

Chrome 从 150 版开始允许扩展把菜单项加进**标签栏右键菜单**（`chrome.contextMenus` 的 `"tab"` 上下文）。TabClip 就是最小、最干净地利用这一点：不弹窗、不跳页、不接管新标签页，只在标签栏的右键菜单里多两行，点一下就复制。

```
┌─────────────────────────────┐
│  重新加载                    │
│  复制                        │
│  固定                        │
│  ...                        │
│  复制选中标签页的 URL          │  ← TabClip
│  复制选中标签页的标题 + URL     │  ← TabClip
│  关闭其他标签页               │
└─────────────────────────────┘
```

## 功能

- **只复制选中的标签**：按住 `Cmd`（macOS）/ `Ctrl`（Windows/Linux）间隔多选，或 `Shift` 连续多选，然后在**其中一个选中的标签**上右键。
- **两种格式**：纯 URL（一行一个）/ `标题 + URL`。
- **按标签栏顺序**输出，不是按点击顺序。
- **三种入口**：
  - 标签栏右键菜单（Chrome 150+）
  - 网页内右键菜单（所有版本，兜底）
  - 工具栏图标 / 快捷键 `Alt+Shift+C`（复制当前窗口选中的标签）
- **即时反馈**：复制成功后工具栏图标短暂显示复制了几个标签，失败显示红色 `!`。
- **零权限焦虑**：只用 `tabs`、`contextMenus`、`clipboardWrite`、`offscreen`，不发任何网络请求，不收集任何数据。

## 安装（开发者模式）

1. 打开 `chrome://extensions`
2. 右上角打开 **开发者模式 / Developer mode**
3. 点 **加载已解压的扩展程序 / Load unpacked**，选择本仓库根目录
4. 完成。不需要构建，纯原生 JS

> 需要 **Chrome 150+** 才有标签栏右键菜单。低版本仍可用网页右键 / 工具栏图标 / 快捷键。

## 使用

1. 多选标签页（`Cmd`/`Ctrl` 或 `Shift`）
2. 在**已选中的标签**上点右键
3. 选「复制选中标签页的 URL」

复制结果示例：

```
https://github.com/ursasi/tabclip
https://developer.chrome.com/docs/extensions/reference/api/contextMenus
https://developer.chrome.com/docs/extensions/reference/api/tabs
```

## 为什么右键要落在“已选中”的标签上

这是 Chrome 自身的行为：右键一个**未选中**的标签，会把当前的多选收缩成它自己。所以想复制多个，右键时必须点在已经高亮的标签上。TabClip 只是把当前高亮的标签全部读出来。

## 原理 / How it works

1. `chrome.contextMenus.create({ contexts: ["tab"] })` 把菜单项注册到标签栏右键菜单（[Chrome 150+](https://developer.chrome.com/docs/extensions/whats-new)）。
2. 点击回调拿到右键所在窗口的 `windowId`。
3. `chrome.tabs.query({ highlighted: true, windowId })` 取出该窗口所有高亮/选中的标签，按 `index` 排序。
4. 用 `offscreen` 文档把文本写进剪贴板（MV3 的 service worker 没有 DOM，无法直接用剪贴板 API）。

```
background.js (service worker)
        │  contextMenus.onClicked
        ▼
  tabs.query({highlighted:true, windowId})
        │  join("\n")
        ▼
  runtime.sendMessage → offscreen.html
        │  execCommand("copy") / navigator.clipboard
        ▼
     剪贴板 ✅
```

## 文件结构

```
tabclip/
├── manifest.json      # MV3 清单
├── background.js      # 注册菜单 + 取选中标签 + 写剪贴板
├── offscreen.html     # 剪贴板用的隐藏文档
├── offscreen.js       # 实际的复制逻辑
├── icons/             # 16/32/48/128/256 PNG
├── tools/gen_icons.py # 图标生成脚本（纯标准库，可复现）
└── docs/banner.svg    # README 头图
```

## 开发

改完代码后，在 `chrome://extensions` 里点扩展卡片上的 **↻ 重新加载**。

调试——在 `chrome://extensions` 打开本扩展的 **Service Worker** 控制台，可以看到 `background.js` 的日志（例如写剪贴板失败会打印 `写剪贴板失败:`）。

重新生成图标：

```bash
python3 tools/gen_icons.py
```

## 常见问题

**菜单里看不到 TabClip？**
Chrome 版本低于 150。升级 Chrome，或改用网页右键菜单 / 工具栏图标。

**复制出来只有一个 URL？**
右键时点在未选中的标签上了，Chrome 把多选收缩了。请右键**已高亮的标签**。

**点了没反应？**
打开 Service Worker 控制台看报错。大多是剪贴板被系统/其他软件占用，重试即可。

## 许可

MIT，见 [LICENSE](LICENSE)。

## 相关

- 如果你只想导出「整个窗口 / 全部标签」并且需要 JSON、CSV 等格式，[Tab Copy](https://chromewebstore.google.com/detail/tab-copy/micdllihgoppmejpecmkilggmaagfdmb) 更合适。
- TabClip 的定位是：**只复制你选中的那几个**，一个动作，零干扰。
