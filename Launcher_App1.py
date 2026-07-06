import urllib.request
import os
import tempfile
import sys

# --- ⚠️ จุดสำคัญที่แก้ปัญหา No module named 'tkinter' และ 'ctypes' 100% ---
# เราต้อง import โมดูล GUI และทุกตัวที่โปรแกรมจริง (Main.py) ของคุณใช้เอาไว้ตรงนี้!
# เพื่อให้ PyInstaller รู้และดึง DLL ต่างๆ ฝังเข้าไปในไฟล์ .exe ด้วย

# 1. กลุ่ม GUI (Tkinter)
import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog

# 2. กลุ่มจัดการระบบและ DLLs (แก้ปัญหา No module named 'ctypes')
import ctypes
import ctypes.util

# 💡 หมายเหตุสำคัญ: 
# จากภาพโค้ด Main.py ใน GitHub ของคุณก่อนหน้านี้ เห็นว่ามีการใช้ numpy, pywin32 และอื่นๆ
# หากตัว Launcher นี้ไม่ได้มีระบบโหลดให้อัตโนมัติและต้องการให้ .exe นี้มีครบจบในตัว 
# อย่าลืม import เพิ่มไว้ตรงนี้ด้วยนะครับ เช่น:
# import numpy
# import win32api
# import win32con
# ---------------------------------------------------------------------------------

# เอาลิงก์ Raw URL ของไฟล์หลักที่ 1 บน GitHub มาวางตรงนี้
GITHUB_RAW_URL = "https://raw.githubusercontent.com/suriwrrnkulchang-art/55/refs/heads/main/Main.py"

temp_dir = tempfile.gettempdir()
TEMP_FILE = os.path.join(temp_dir, "downloaded_script_1.py")

try:
    print("กำลังตรวจสอบและดึงไฟล์อัปเดตล่าสุดจาก GitHub (App 1)...")
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
