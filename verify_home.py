import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Log all console messages
        page.on("console", lambda msg: print(f"Console {msg.type}: {msg.text}"))

        # Log failed network requests
        page.on("requestfailed", lambda request: print(f"Request failed: {request.url} - {request.failure.error_text}"))
        page.on("response", lambda response: print(f"Response: {response.url} - {response.status}") if response.status >= 400 else None)

        print("Navigating to http://127.0.0.1:5000/")
        await page.goto("http://127.0.0.1:5000/", wait_until="networkidle")

        # Get all img tags and their src/naturalWidth
        imgs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('img')).map(img => ({
                src: img.src,
                naturalWidth: img.naturalWidth,
                naturalHeight: img.naturalHeight,
                complete: img.complete,
                alt: img.alt,
                className: img.className
            }));
        }''')
        print("Images found on page:")
        for img in imgs:
            print(img)

        await page.screenshot(path="home_page_debug.png", full_page=True)
        await browser.close()

asyncio.run(run())
