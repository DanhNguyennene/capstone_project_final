"""Render a .mmd file to PNG using Playwright + Mermaid.js."""
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright


def build_html(mmd_source: str) -> str:
    return (
        '<!DOCTYPE html><html><body>'
        '<pre class="mermaid">' + mmd_source + '</pre>'
        '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>'
        '<script>mermaid.initialize({startOnLoad:true, theme:"neutral"});</script>'
        '</body></html>'
    )


async def main(input_path: str, output_path: str):
    mmd_source = Path(input_path).read_text(encoding="utf-8")
    html = build_html(mmd_source)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 2400, "height": 1600}, device_scale_factor=2)
        await page.set_content(html)
        await page.wait_for_selector("svg", timeout=15000)
        await asyncio.sleep(1)
        el = await page.query_selector("pre.mermaid svg")
        if not el:
            el = await page.query_selector("svg")
        await el.screenshot(path=output_path)
        await browser.close()
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "request_lifecycle_flow.mmd"
    out = sys.argv[2] if len(sys.argv) > 2 else "images/request_lifecycle_flow.png"
    asyncio.run(main(inp, out))
