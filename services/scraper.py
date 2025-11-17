import asyncio
from playwright.async_api import async_playwright, BrowserContext, Page, Request
import json
import re # Import re for regular expressions
import os

async def connect_to_browser(port: int = 9222) -> BrowserContext:
    """
    Tries to connect to a running browser. If it fails, launches a new
    persistent browser instance by trying a sequence of common browsers.
    """
    playwright = await async_playwright().start()

    # 1. Try to connect to an existing browser instance first
    try:
        browser = await playwright.chromium.connect_over_cdp(f"http://localhost:{port}")
        print(f"Successfully connected to existing browser on port {port}.")
        if browser.contexts:
            return browser.contexts[0]
        print("No browser contexts found in the existing browser. Will attempt to launch a new one.")
    except Exception:
        print(f"Could not connect to a browser on port {port}. Launching a new browser instance.")

    # 2. If connection fails, try to launch a sequence of system browsers
    user_data_dir = os.path.join(os.getcwd(), 'playwright_user_data')
    browser_channels_to_try = [
        {"channel": "msedge", "name": "Microsoft Edge"},
        {"channel": "chrome", "name": "Google Chrome"},
    ]

    for browser_info in browser_channels_to_try:
        try:
            print(f"Attempting to launch {browser_info['name']}...")
            context = await playwright.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                channel=browser_info["channel"],
                args=['--disable-blink-features=AutomationControlled']
            )
            print(f"Successfully launched {browser_info['name']}. User data is stored in: {user_data_dir}")
            return context
        except Exception:
            print(f"Could not launch {browser_info['name']}. Trying next available browser.")
            continue

    # 3. If all system browsers fail, fall back to Playwright's default Chromium
    try:
        print("Could not find Edge or Chrome. Attempting to launch Playwright's default Chromium browser.")
        print("If this fails, please run 'playwright install chromium'")
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        print(f"Successfully launched Playwright's Chromium. User data is stored in: {user_data_dir}")
        return context
    except Exception as e:
        print(f"Fatal: Failed to launch any browser. Please ensure a compatible browser is installed and/or run 'playwright install'. Error: {e}")
        await playwright.stop()
        return None

async def get_active_page(context: BrowserContext) -> Page:
    """
    Gets the most recently active page from the browser context.
    """
    if not context.pages:
        print("No pages found in the browser context. Make sure a tab is open.")
        return None
    return context.pages[-1]

async def fetch_ticket_data(page: Page, target_url: str) -> dict:
    """
    Navigates to the target URL, extracts the 'zone' JSON data from the page content.
    """
    try:
        await page.goto(target_url, wait_until="networkidle")
        content = await page.content()
        content = content.encode().decode('unicode_escape')

        start_index = content.find("var zone = {")
        if start_index != -1:
            start_index += len("var zone = ")
            brace_count = 0
            end_index = -1
            for i in range(start_index, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_index = i + 1
                        break
            
            if end_index != -1:
                json_str = content[start_index:end_index].strip()
                try:
                    data = json.loads(json_str)
                    return {"zone": data} # Wrap in a 'zone' key to match check_ticket_availability
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from page content: {e}")
                    return {}
            else:
                print("Could not find the end of the 'zone' JSON object.")
                return {}
        else:
            print("Could not find 'var zone = {' in the page content.")
            return {}

    except Exception as e:
        print(f"Error navigating to or parsing page {target_url}: {e}")
        return {}

async def check_ticket_availability(data: dict, selected_codes: list[str]) -> tuple[bool, list[str]]:
    """
    Checks if tickets are available in the selected areas.
    Returns a tuple: (bool: True if any are available, list: names of available areas).
    """
    if not data or "zone" not in data:
        print("Invalid or empty ticket data received.")
        return False, []

    available_areas = []
    all_zones = data["zone"]

    # If no specific codes are selected, check all of them
    codes_to_check = selected_codes if selected_codes else all_zones.keys()

    for area_code in codes_to_check:
        if area_code in all_zones:
            area_info = all_zones[area_code]
            if "areaStatus" in area_info and area_info["areaStatus"] != "UNAVAILABLE":
                available_areas.append(area_info.get('description', area_code))

    if available_areas:
        return True, available_areas
    
    return False, []