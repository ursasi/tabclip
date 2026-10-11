#!/usr/bin/env python3
"""Generate the English-annotated screenshot for the README.

Reads  docs/screenshot-raw.png  (the raw capture)
Writes docs/screenshot.png      (same shot + numbered English callouts)

Renders an HTML page with headless Chrome so the callouts use real fonts.
Requires Google Chrome. Usage:

    python3 tools/annotate_screenshot.py
"""
import base64
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
RAW = os.path.join(ROOT, "docs", "screenshot-raw.png")
OUT = os.path.join(ROOT, "docs", "screenshot.png")

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("chromium-browser") or "",
]

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #ffffff;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                       Helvetica, Arial, "PingFang SC", "Microsoft YaHei", sans-serif; }}
  .canvas {{ width: 940px; padding: 22px 35px 26px; }}
  .title {{ font-size: 21px; font-weight: 700; color: #0f172a; text-align: center; }}
  .subtitle {{ font-size: 13px; color: #64748b; text-align: center; margin-top: 4px; }}
  .wrap {{ position: relative; width: 870px; margin: 16px auto 0; }}
  .wrap img {{ display: block; width: 870px; border-radius: 10px;
               box-shadow: 0 6px 22px rgba(15,23,42,.18); }}
  .badge {{ position: absolute; width: 27px; height: 27px; border-radius: 50%;
            background: #6366f1; color: #fff; font-size: 15px; font-weight: 700;
            line-height: 27px; text-align: center;
            box-shadow: 0 0 0 3px #fff, 0 2px 6px rgba(15,23,42,.35); }}
  .b1 {{ left: 11px;  top: 243px; }}
  .b2 {{ left: 826px; top: 258px; }}
  .legend {{ width: 870px; margin: 18px auto 0; font-size: 13.5px;
             line-height: 1.7; color: #1e293b; }}
  .legend b {{ color: #4338ca; }}
  .num {{ display: inline-block; width: 20px; height: 20px; border-radius: 50%;
          background: #6366f1; color: #fff; font-size: 12px; font-weight: 700;
          line-height: 20px; text-align: center; margin-right: 6px; }}
  code {{ background: #f1f5f9; border-radius: 4px; padding: 1px 5px;
          font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12.5px; }}
</style></head><body>
  <div class="canvas">
    <div class="title">TabClip in the tab-strip right-click menu</div>
    <div class="subtitle">Select tabs &rarr; right-click one of them &rarr; TabClip &rarr; copy</div>
    <div class="wrap">
      <img src="data:image/png;base64,{b64}" alt="TabClip menu">
      <div class="badge b1">1</div>
      <div class="badge b2">2</div>
    </div>
    <div class="legend">
      <div><span class="num">1</span><b>TabClip</b> shows up directly in the tab strip's right-click menu.
        Chrome nests every extension's items under a submenu named after the extension.</div>
      <div><span class="num">2</span>Pick a format &mdash; <code>Copy selected tab URLs</code> for plain
        URLs, or <code>titles + URLs</code> when you want the page titles too.</div>
    </div>
  </div>
</body></html>
"""


def main():
    if not os.path.exists(RAW):
        sys.exit(f"missing {RAW}")
    chrome = next((c for c in CHROME_CANDIDATES if c and os.path.exists(c)), None)
    if not chrome:
        sys.exit("Google Chrome not found; install it or edit CHROME_CANDIDATES")

    b64 = base64.b64encode(open(RAW, "rb").read()).decode()
    html_path = os.path.join("/tmp", "tabclip_annotate.html")
    open(html_path, "w", encoding="utf-8").write(HTML.format(b64=b64))

    subprocess.run(
        [
            chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=2", "--window-size=940,470",
            "--virtual-time-budget=3000", f"--screenshot={OUT}", f"file://{html_path}",
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print("wrote", OUT)


if __name__ == "__main__":
    main()
