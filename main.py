import asyncio
import json
import time
import sys
from contextlib import redirect_stdout
from models import Config
from services.scraper import connect_to_browser, get_active_page, fetch_ticket_data, check_ticket_availability
from services.notifier import send_notification_email

def generate_default_config():
    """Generates a default config.json file."""
    default_config = {
      "send_email_notifications": True,
      "check_interval_seconds": 30,
      "smtp_server": "smtp.example.com",
      "smtp_port": 587,
      "smtp_user": "your_email@example.com",
      "smtp_password": "your_app_password"
    }
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2, ensure_ascii=False)
    print("Default 'config.json' has been generated.")
    print("Please edit 'config.json' with your actual settings before running again.")


async def main_logic(target_url):
    """Main logic for the ticket checker, separated for clarity."""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        config = Config(**config_data)
        config.target_url = target_url
        print("Configuration loaded successfully.")
    except FileNotFoundError:
        print("'config.json' not found.")
        generate_default_config()
        return
    except Exception as e:
        print(f"Error loading or parsing config.json: {e}")
        print("Please ensure config.json is correctly formatted.")
        return

    print("Attempting to connect to your running browser (Edge/Chrome)...")
    browser_context = await connect_to_browser()

    if not browser_context:
        print("Could not establish connection. Exiting.")
        return

    active_page = await get_active_page(browser_context)

    if not active_page:
        print("Could not find an active page to attach to. Exiting.")
        return

    print(f"Connected to page: '{await active_page.title()}' at {active_page.url}")

    # --- Area Selection Logic ---
    print("\nFetching available areas...")
    initial_ticket_data = await fetch_ticket_data(active_page, str(config.target_url))
    if not initial_ticket_data or "zone" not in initial_ticket_data:
        print("Could not fetch area information. Exiting.")
        return

    all_areas = initial_ticket_data["zone"]
    print("--- Available Areas ---")
    for i, (area_code, area_info) in enumerate(all_areas.items()):
        print(f"  [{i+1}] {area_info.get('description', area_code)} (Status: {area_info.get('areaStatus', 'N/A')})")
    print("-----------------------")

    selected_indices = input("请输入您要监控的场地编号 (多个请用逗号隔开, 或直接按回车监控所有): ")
    selected_area_codes = []
    if selected_indices:
        try:
            indices = [int(i.strip()) - 1 for i in selected_indices.split(',')]
            all_area_keys = list(all_areas.keys())
            selected_area_codes = [all_area_keys[i] for i in indices]
            print(f"Now monitoring selected areas: {[all_areas[code].get('description', code) for code in selected_area_codes]}")
        except (ValueError, IndexError):
            print("无效的输入，将监控所有场地。")
            selected_area_codes = list(all_areas.keys())
    else:
        print("将监控所有场地。")
        selected_area_codes = list(all_areas.keys())
    # --- End of Area Selection ---

    while True:
        print(f"\n--- Checking for tickets at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
        ticket_data = await fetch_ticket_data(active_page, str(config.target_url))

        if not ticket_data:
            print(f"Failed to fetch ticket data. Retrying in {config.check_interval_seconds} seconds...")
            await asyncio.sleep(config.check_interval_seconds)
            continue

        is_available, available_areas = await check_ticket_availability(ticket_data, selected_area_codes)

        if is_available:
            print(f"!!! Tickets are AVAILABLE in: {available_areas} !!!") # Print detailed areas
            print(f"Sending notification...") # Separate line for clarity
            if config.send_email_notifications:
                subject = "Ticket Available Notification"
                body = f"Tickets are now available in the following areas: {available_areas}\nURL: {config.target_url}"
                success = send_notification_email(config, subject, body)
                if not success:
                    print("Email notification failed. Will retry...")
            else:
                print("Email notifications are disabled in config.json. Not sending email.")
        else:
            print(f"Tickets are still unavailable in selected areas. Checking again in {config.check_interval_seconds} seconds...")
        
        await asyncio.sleep(config.check_interval_seconds)

if __name__ == "__main__":
    # Prompt for URL at runtime
    target_url = input("请输入您要监控的抢票网址: ")
    if not target_url:
        print("URL不能为空，程序退出。")
        sys.exit(1)

    # URL transformation logic
    if "/ticket/area/" in target_url:
        target_url = target_url.replace("/ticket/area/", "/ticket/get-area-map/")

    asyncio.run(main_logic(target_url))
