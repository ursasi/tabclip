# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.1.0] - 2026-10-11

### Added
- 国际化：`_locales/en` + `_locales/zh_CN`，扩展名称、描述、右键菜单、快捷键说明、offscreen 理由全部跟随浏览器界面语言自动切换。
- `manifest.json` 增加 `"default_locale": "en"`，缺省语言为英文。
- 英文注释版截图（`docs/screenshot.png`）与生成脚本 `tools/annotate_screenshot.py`。

### Changed
- 菜单文案不再写死中文，改用 `chrome.i18n.getMessage()`。

## [1.0.0] - 2026-10-11

### Added
- 标签栏右键菜单（Chrome 150+ 的 `"tab"` 上下文）：复制选中标签页的 URL、标题 + URL。
- 网页右键菜单兜底入口。
- 工具栏图标点击、快捷键 `Alt+Shift+C` 复制当前窗口选中的标签。
- 复制结果按标签栏顺序排列，一行一个。
- 通过 offscreen 文档写剪贴板（MV3）。
- 工具栏角标反馈复制数量 / 失败提示。
- 脚本生成的渐变图标（16/32/48/128/256）。
