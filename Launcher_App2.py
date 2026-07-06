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
MUTEX_NAME = "Global\\FilterCore_App2_SingleInstanceMutex"
mutex = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
    sys.exit(0)

GITHUB_RAW_URL = "https://raw.githubusercontent.com/suriwrrnkulchang-art/55/refs/heads/main/uninstall.py"
EXPECTED_SHA256 = "5cb2a9d17c6f1e6894c9c549e59df4eb99c93b9bb4c8cfb5f38cea141a06d338"

# 🛡️ เครื่องหมายที่ต้องมีในไฟล์ตัวถอนการติดตั้งจริง (ป้องกันดาวน์โหลด/รันไฟล์ผิด)
REQUIRED_MARKERS = ["load_install_info", "remove_install_dir", "uninstall_pip_packages"]
FORBIDDEN_MARKERS = ["class InstallerApp", "GITHUB_ZIP_URL"]

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

    with open(TEMP_FILE, "r", encoding="utf-8") as f:
        downloaded_code = f.read()

    # 🛡️ ตรวจสอบเนื้อหาว่าเป็นไฟล์ถอนการติดตั้งจริง ไม่ใช่ไฟล์ติดตั้งที่อัปโหลดผิด
    missing = [m for m in REQUIRED_MARKERS if m not in downloaded_code]
    wrong_file = [m for m in FORBIDDEN_MARKERS if m in downloaded_code]

    if missing or wrong_file:
        print("❌ ไฟล์ที่ดาวน์โหลดมาไม่ใช่ไฟล์ 'ตัวถอนการติดตั้ง' ที่ถูกต้อง!")
        if wrong_file:
            print("   ดูเหมือนว่าไฟล์นี้เป็นโค้ด 'ตัวติดตั้ง' (install.py) ไม่ใช่ตัวถอนการติดตั้ง")
        if missing:
            print(f"   ไม่พบส่วนที่ควรมี: {', '.join(missing)}")
        print("   กรุณาตรวจสอบไฟล์ uninstall.py บน GitHub ว่าอัปโหลดถูกไฟล์หรือไม่")
        input("กด Enter เพื่อปิดโปรแกรม...")
        sys.exit(1)

    print("กำลังเริ่มทำงาน...")
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
