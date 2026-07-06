import urllib.request
import os
import tempfile
import sys

# --- ⚠️ จุดสำคัญที่แก้ปัญหา No module named 'tkinter' และ 'ctypes' 100% ---
# 1. กลุ่ม GUI (Tkinter)
import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog

# 2. กลุ่มจัดการระบบและ DLLs
import ctypes
import ctypes.util
# ---------------------------------------------------------------------------------

# 🟢 เปลี่ยนลิงก์ Raw URL ตรงนี้ให้เป็นไฟล์ Main ตัวที่ 2 ของคุณบน GitHub
GITHUB_RAW_URL = "https://raw.githubusercontent.com/suriwrrnkulchang-art/55/refs/heads/main/Main2.py"

temp_dir = tempfile.gettempdir()
TEMP_FILE = os.path.join(temp_dir, "downloaded_script_2.py")

try:
    print("กำลังตรวจสอบและดึงไฟล์อัปเดตล่าสุดจาก GitHub (App 2)...")
    urllib.request.urlretrieve(GITHUB_RAW_URL, TEMP_FILE)
    
    print("กำลังเริ่มทำงาน...")
    with open(TEMP_FILE, "r", encoding="utf-8") as f:
        downloaded_code = f.read()
    
    # รันโค้ดที่ดาวน์โหลดมาทันทีโดยไม่ต้องเปิดไฟล์ซ้อน
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
