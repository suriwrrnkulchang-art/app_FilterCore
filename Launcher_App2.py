import urllib.request
import os
import tempfile
import sys
import hashlib
import json

# --- ⚠️ จุดสำคัญที่แก้ปัญหา No module named 'tkinter' และ 'ctypes' 100% ---
import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog
import ctypes
import ctypes.util
# import numpy
# import win32api
# import win32con

# 🟢 ใส่ลิงก์ Raw URL ของไฟล์หลักที่ 2 บน GitHub (เปลี่ยนเป็นไฟล์จริงของ App2)
GITHUB_RAW_URL = "https://raw.githubusercontent.com/suriwrrnkulchang-art/55/refs/heads/main/uninstall.py"

# 🔒 SHA-256 hash ของไฟล์เวอร์ชันที่เชื่อถือได้ (ของ App2)
EXPECTED_SHA256 = "aa7f1b9622dbe0c2b164259af5432fab34122c81f13d3cf56c00c5ff7fcc227c"

temp_dir = tempfile.gettempdir()
TEMP_FILE = os.path.join(temp_dir, "downloaded_script_2.py")


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


try:
    print("กำลังตรวจสอบและดึงไฟล์อัปเดตล่าสุดจาก GitHub (App 2)...")
    urllib.request.urlretrieve(GITHUB_RAW_URL, TEMP_FILE)

    actual_hash = sha256_of_file(TEMP_FILE)

    if EXPECTED_SHA256 == "ใส่ hash ของไฟล์ App2 ที่นี่":
        print("⚠️ ยังไม่ได้ตั้งค่า EXPECTED_SHA256 — ข้ามการตรวจสอบ (ไม่แนะนำสำหรับใช้งานจริง)")
    elif actual_hash != EXPECTED_SHA256:
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
