import sys

if sys.stdout is not None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr is not None:
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import urllib.request
import urllib.error
import os
import tempfile
import hashlib
import json
import time

import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog
import ctypes
import ctypes.util
# import numpy
# import win32api
# import win32con

# 🔒 ป้องกันการรันซ้ำ — ถ้ามีตัวเดิมรันอยู่แล้ว ให้ปิดตัวเองเงียบๆ ทันที ไม่แจ้งเตือน
MUTEX_NAME = "Global\\FilterCore_App1_SingleInstanceMutex"
mutex = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
    sys.exit(0)

GITHUB_RAW_URL = "https://raw.githubusercontent.com/suriwrrnkulchang-art/55/refs/heads/main/install.py"
EXPECTED_SHA256 = "e0df9e8cf57c8b661356b9dab4dc3794eed062247de4f06e392fade15e62f33"

# ปลอมตัวเป็นเบราว์เซอร์ตอนดาวน์โหลด กันบางกรณีที่ proxy/CDN ตอบผิดปกติ
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36"

temp_dir = tempfile.gettempdir()
TEMP_FILE = os.path.join(temp_dir, "downloaded_script_1.py")


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def download_with_retry(url, dest_path, max_tries=6):
    """
    ดาวน์โหลดไฟล์ พร้อม retry อัตโนมัติเมื่อเจอ:
      - HTTP 429 (Too Many Requests) -> รอตาม Retry-After (ถ้ามี) หรือ backoff แบบเพิ่มเวลาไปเรื่อยๆ
      - HTTP 5xx (server error ชั่วคราว)
      - ปัญหาเครือข่ายทั่วไป (URLError)
    """
    last_err = None
    for attempt in range(1, max_tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            with open(dest_path, "wb") as f:
                f.write(data)
            return  # สำเร็จ ออกจากฟังก์ชันทันที

        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 429:
                retry_after = e.headers.get("Retry-After")
                if retry_after:
                    try:
                        wait_time = int(retry_after)
                    except ValueError:
                        wait_time = 5 * attempt
                else:
                    wait_time = min(5 * attempt, 30)  # ค่อยๆ เพิ่มเวลารอ สูงสุด 30 วิ
                print(f"⏳ GitHub จำกัดการดาวน์โหลดชั่วคราว (429) กำลังรอ {wait_time} วินาที แล้วลองใหม่... "
                      f"(ครั้งที่ {attempt}/{max_tries})")
                time.sleep(wait_time)
                continue
            elif 500 <= e.code < 600:
                wait_time = min(3 * attempt, 20)
                print(f"⏳ เซิร์ฟเวอร์มีปัญหาชั่วคราว ({e.code}) กำลังรอ {wait_time} วินาที แล้วลองใหม่... "
                      f"(ครั้งที่ {attempt}/{max_tries})")
                time.sleep(wait_time)
                continue
            else:
                # error อื่นๆ (เช่น 404 ไฟล์ไม่พบ) ไม่มีประโยชน์ที่จะลองซ้ำ
                raise

        except urllib.error.URLError as e:
            last_err = e
            wait_time = min(3 * attempt, 20)
            print(f"⏳ เชื่อมต่อเครือข่ายไม่ได้ กำลังรอ {wait_time} วินาที แล้วลองใหม่... "
                  f"(ครั้งที่ {attempt}/{max_tries})")
            time.sleep(wait_time)
            continue

    raise RuntimeError(f"ดาวน์โหลดไม่สำเร็จหลังจากลอง {max_tries} ครั้ง: {last_err}")


try:
    print("กำลังตรวจสอบและดึงไฟล์อัปเดตล่าสุดจาก GitHub (App 1)...")
    download_with_retry(GITHUB_RAW_URL, TEMP_FILE)

    actual_hash = sha256_of_file(TEMP_FILE)

    if actual_hash != EXPECTED_SHA256:
        print("❌ ไฟล์ที่ดาวน์โหลดมาไม่ตรงกับ hash ที่กำหนดไว้!")
        print(f"   คาดหวัง: {EXPECTED_SHA256}")
        print(f"   ได้จริง: {actual_hash}")
        print("   จะไม่รันไฟล์นี้เพื่อความปลอดภัย")
        input("กด Enter เพื่อปิดโปรแกรม...")
        sys.exit(1)

    print("กำลังเริ่มทำงาน...")
    with open(TEMP_FILE, "r", encoding="utf-8") as f:
        downloaded_code = f.read()

    exec(downloaded_code, globals())

except Exception as e:
    print(f"เกิดข้อผิดพลาดในการรันระบบ: {e}")
    print("💡 หากปัญหานี้เกิดซ้ำๆ ลองรอสัก 5-10 นาทีแล้วเปิดโปรแกรมใหม่อีกครั้ง")
    input("กด Enter เพื่อปิดโปรแกรม...")
finally:
    if os.path.exists(TEMP_FILE):
        try:
            os.remove(TEMP_FILE)
        except:
            pass
