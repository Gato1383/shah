#!/usr/bin/env python3
# ZEUS Proxy Fetcher - Termux
# Fetches raw country subscription files and prints their proxy rows
# with the same line numbers as the GitHub code view.

import shutil
import subprocess
import urllib.error
import urllib.request

ROOT = "https://raw.githubusercontent.com/panel-zeus/Z-E-U-S/main/"
SOURCES = {
    "1": ("STANDARD", ROOT + "proxy/"),
    "2": ("VIP", ROOT + "proxy_vip/"),
}

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"


def clear_screen():
    print("\033[2J\033[H", end="")


def copy_to_clipboard(proxies):
    """Copy plain proxy addresses (without display line numbers) to Android clipboard."""
    clipboard_cmd = shutil.which("termux-clipboard-set")
    if not clipboard_cmd:
        print(f"\n{YELLOW}[CLIPBOARD] termux-clipboard-set was not found; copy skipped.{RESET}")
        return False

    try:
        payload = "\n".join(proxy for _, proxy in proxies) + "\n"
        result = subprocess.run(
            [clipboard_cmd],
            input=payload,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
        if result.returncode == 0:
            print(f"\n{GREEN}[COPIED] {len(proxies)} proxy addresses copied to Android clipboard.{RESET}")
            return True

        detail = result.stderr.strip() or result.stdout.strip()
        suffix = f": {detail}" if detail else "."
        print(f"\n{RED}[CLIPBOARD ERROR] Copy command failed{suffix}{RESET}")
    except Exception as exc:
        print(f"\n{RED}[CLIPBOARD ERROR] {type(exc).__name__}: {exc}{RESET}")
    return False


def fetch_and_print(folder_url, filename):
    # Raw file endpoint: only the actual text inside GitHub's code box.
    url = folder_url + filename
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ZEUS-Termux-Proxy-Fetcher/3.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read().decode("utf-8-sig", errors="replace")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            print(f"\n{RED}[NOT FOUND] {filename} is not available in this folder.{RESET}")
        else:
            print(f"\n{RED}[HTTP ERROR] {exc.code}: {exc.reason}{RESET}")
        return
    except urllib.error.URLError as exc:
        print(f"\n{RED}[NETWORK ERROR] {exc.reason}{RESET}")
        return
    except TimeoutError:
        print(f"\n{RED}[TIMEOUT] GitHub did not respond within 30 seconds.{RESET}")
        return
    except Exception as exc:
        print(f"\n{RED}[ERROR] {type(exc).__name__}: {exc}{RESET}")
        return

    rows = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        value = line.strip()
        if value and not value.startswith("#"):
            rows.append((line_number, value))

    print()
    if not rows:
        print(f"{YELLOW}[NO PROXY ROWS] The selected file is empty.{RESET}")
        return

    # Keep original GitHub line numbers; do not renumber after filtering.
    for line_number, proxy in rows:
        print(f"{WHITE}{line_number:>4}  {proxy}{RESET}")

    print(f"\n{GREEN}{BOLD}TOTAL: {len(rows)} PROXY LINES{RESET}")
    copy_to_clipboard(rows)


def subscription_menu(name, folder_url):
    while True:
        print(f"\n{MAGENTA}{BOLD}========== {name} =========={RESET}")
        print(f"{CYAN}1.{WHITE} Country file (DE, US, TR, AU...)")
        print(f"{CYAN}2.{WHITE} ALL.txt")
        print(f"{CYAN}3.{WHITE} Back to MAIN MENU")
        print(f"{CYAN}4.{WHITE} Exit")
        choice = input(f"\n{YELLOW}Choose [1-4]: {RESET}").strip()

        if choice == "1":
            country = input(f"{YELLOW}Country code: {RESET}").strip().upper()
            if len(country) != 2 or not country.isascii() or not country.isalpha():
                print(f"{RED}Enter exactly two English letters, e.g. DE.{RESET}")
                continue
            fetch_and_print(folder_url, country + ".txt")
            input(f"\n{CYAN}Press ENTER to continue...{RESET}")
        elif choice == "2":
            fetch_and_print(folder_url, "ALL.txt")
            input(f"\n{CYAN}Press ENTER to continue...{RESET}")
        elif choice == "3":
            return
        elif choice == "4":
            raise SystemExit
        else:
            print(f"{RED}Invalid option.{RESET}")


def main():
    while True:
        clear_screen()
        print(f"{CYAN}{BOLD}")
        print("==============================================")
        print("             ZEUS PROXY FETCHER")
        print("==============================================")
        print(f"{RESET}{MAGENTA}{BOLD}MAIN MENU{RESET}")
        print(f"{GREEN}1.{WHITE} STANDARD SUB  {YELLOW}(proxy)")
        print(f"{GREEN}2.{WHITE} VIP SUB       {YELLOW}(proxy_vip)")
        print(f"{GREEN}3.{WHITE} EXIT")
        choice = input(f"\n{YELLOW}Choose [1-3]: {RESET}").strip()

        if choice in SOURCES:
            name, folder_url = SOURCES[choice]
            subscription_menu(name, folder_url)
        elif choice == "3":
            print(f"\n{GREEN}Exit.{RESET}")
            return
        else:
            print(f"{RED}Invalid option.{RESET}")
            input(f"{CYAN}Press ENTER to continue...{RESET}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Stopped by user.{RESET}")
