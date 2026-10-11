chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg && msg.target === "offscreen" && msg.type === "copy" && typeof msg.text === "string") {
    // offscreen 文档通常没有焦点，execCommand 比 navigator.clipboard 更稳，先试它
    if (legacyCopy(msg.text)) {
      sendResponse({ ok: true });
      return true;
    }
    navigator.clipboard.writeText(msg.text).then(
      () => sendResponse({ ok: true }),
      (e) => sendResponse({ ok: false, error: String(e) })
    );
    return true; // 异步
  }
});

function legacyCopy(text) {
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.setAttribute("readonly", "");
  ta.style.position = "fixed";
  ta.style.top = "0";
  ta.style.left = "0";
  ta.style.opacity = "0";
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  ta.setSelectionRange(0, text.length);
  let ok = false;
  try {
    ok = document.execCommand("copy");
  } catch (_) {
    ok = false;
  }
  ta.remove();
  return ok;
}
