// 复制选中标签页的 URL（Manifest V3）
//
// 右键菜单同时注册在：
//   - "tab"  标签栏右键（Chrome 150+，和 SingleFile 同款位置）
//   - "page" 网页右键（旧版 Chrome 兜底）
//
// 点击后：取右键所在窗口里所有「高亮/选中」的标签 -> 按标签顺序拼成文本 -> 写剪贴板。

const MENUS = [
  // [id, i18n message key, 是否带标题, context]
  ["copy-urls-tab", "menuCopyUrls", false, "tab"],
  ["copy-titles-tab", "menuCopyTitlesAndUrls", true, "tab"],
  ["copy-urls-page", "menuCopyUrls", false, "page"],
  ["copy-titles-page", "menuCopyTitlesAndUrls", true, "page"],
];

// 按浏览器界面语言取文案（Chrome 自动选择 _locales 里最匹配的一种）
const t = (key) => chrome.i18n.getMessage(key) || key;

function buildMenus() {
  chrome.contextMenus.removeAll(() => {
    for (const [id, key, , ctx] of MENUS) {
      chrome.contextMenus.create({ id, title: t(key), contexts: [ctx] }, () => {
        // 旧版 Chrome 不支持 "tab" 上下文时会报错，忽略即可
        void chrome.runtime.lastError;
      });
    }
  });
}

chrome.runtime.onInstalled.addListener(buildMenus);
chrome.runtime.onStartup.addListener(buildMenus);

const WITH_TITLE_BY_ID = Object.fromEntries(MENUS.map((m) => [m[0], m[2]]));

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (!(info.menuItemId in WITH_TITLE_BY_ID)) return;
  copySelected(tab && tab.windowId, WITH_TITLE_BY_ID[info.menuItemId]);
});

// 点工具栏图标 = 复制当前窗口选中的标签
chrome.action.onClicked.addListener(() => copySelected(undefined, false));

// 快捷键 Alt+Shift+C
if (chrome.commands) {
  chrome.commands.onCommand.addListener((cmd) => {
    if (cmd === "copy-selected-urls") copySelected(undefined, false);
  });
}

async function copySelected(windowId, withTitle) {
  const query =
    typeof windowId === "number"
      ? { highlighted: true, windowId }
      : { highlighted: true, currentWindow: true };

  const tabs = (await chrome.tabs.query(query)).sort((a, b) => a.index - b.index);
  if (tabs.length === 0) return;

  const text = tabs
    .map((t) => (withTitle && t.title ? `${t.title}\n${t.url}` : t.url))
    .join("\n");

  const ok = await writeClipboard(text);
  showBadge(ok ? tabs.length : "!", ok);
}

function showBadge(value, ok) {
  chrome.action.setBadgeBackgroundColor({ color: ok ? "#2e7d32" : "#c62828" });
  chrome.action.setBadgeText({ text: String(value) });
  setTimeout(() => chrome.action.setBadgeText({ text: "" }), 1500);
}

// ---- 写剪贴板：MV3 service worker 没有 DOM，用 offscreen 文档 ----
let creatingOffscreen;

async function ensureOffscreen() {
  if (await chrome.offscreen.hasDocument()) return;
  if (creatingOffscreen) return creatingOffscreen;
  creatingOffscreen = chrome.offscreen.createDocument({
    url: "offscreen.html",
    reasons: ["CLIPBOARD"],
    justification: t("offscreenJustification"),
  });
  await creatingOffscreen;
  creatingOffscreen = null;
}

async function writeClipboard(text) {
  try {
    await ensureOffscreen();
    const res = await chrome.runtime.sendMessage({
      target: "offscreen",
      type: "copy",
      text,
    });
    return !!(res && res.ok);
  } catch (e) {
    console.error("写剪贴板失败:", e);
    return false;
  }
}
