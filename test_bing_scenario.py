import asyncio
import json
from pathlib import Path

async def test_bing():
    """Execute bing.com test scenario"""
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        
        try:
            # Step 1: Navigate to bing.com
            print("Step 1: Navigating to https://www.bing.com...")
            await page.goto("https://www.bing.com", wait_until="networkidle")
            print("✅ SUCCESS: browser_navigate completed")
            
            # Step 2: Get page title
            print("\nStep 2: Getting page title...")
            title = await page.title()
            print(f"Page title: {title}")
            if "Bing" in title:
                print("✅ SUCCESS: Page title contains 'Bing'")
            else:
                print(f"❌ FAILED: Page title does not contain 'Bing'")
            
            # Step 3: Verify search box exists
            print("\nStep 3: Verifying search box exists...")
            search_selectors = [
                "textarea[name='q']",
                "#sb_form_q",
                "input[type='search']",
                "[role='searchbox']"
            ]
            
            search_box_found = False
            for selector in search_selectors:
                try:
                    element = page.locator(selector)
                    await element.wait_for(state="visible", timeout=5000)
                    print(f"✅ SUCCESS: Found search box with selector: {selector}")
                    search_box_found = True
                    break
                except Exception as e:
                    print(f"Trying selector {selector}: {str(e)[:50]}...")
                    continue
            
            if not search_box_found:
                print("❌ FAILED: Could not find search box")
            
            # Take screenshot for verification
            screenshot_path = str(Path.cwd() / "bing_test_screenshot.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"\n📸 Screenshot saved to: {screenshot_path}")
            
            print("\n✅ STEP COMPLETED: All test steps executed")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_bing())
