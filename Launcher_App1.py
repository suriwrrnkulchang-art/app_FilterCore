import sys

if sys.stdout is not None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr is not None:
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import urllib.request
import os
import tempfile
import hashlib
import json

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
EXPECTED_SHA256 = "e0df9e8cf57c8b661356b9dab4dc3794eed062247de4f06e392fade15e62f334"

temp_dir = tempfile.gettempdir()
TEMP_FILE = os.path.join(temp_dir, "downloaded_script_1.py")


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


try:
    print("กำลังตรวจสอบและดึงไฟล์อัปเดตล่าสุดจาก GitHub (App 1)...")
    urllib.request.urlretrieve(GITHUB_RAW_URL, TEMP_FILE)

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
    input("กด Enter เพื่อปิดโปรแกรม...")
finally:
    if os.path.exists(TEMP_FILE):
        try:
            os.remove(TEMP_FILE)
        except:
            pass
