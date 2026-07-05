import urllib.request
import os
import tempfile
import sys

# --- ⚠️ จุดสำคัญที่แก้ปัญหา No module named 'tkinter' 100% ---
# เราต้อง import โมดูล GUI และทุกตัวที่โปรแกรมจริงของคุณใช้เอาไว้ตรงนี้ครับ!
# เพื่อให้ PyInstaller รู้และดึง DLL ของ tkinter ฝังเข้าไปในไฟล์ .exe ด้วย
import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog

# 💡 หมายเหตุ: ถ้าในไฟล์โปรแกรมตัดคำจริงๆ ของคุณ มีการใช้คำสั่ง import อื่นๆ อีก 
# เช่น import requests, import PIL, import customtkinter ให้เอามาพิมพ์เพิ่มต่อตรงนี้ได้เลยนะครับ!
# ---------------------------------------------------------------------------------

# เอาลิงก์ Raw URL ของไฟล์หลักบน GitHub มาวางตรงนี้ (อย่าลืมเปลี่ยนลิงก์นะครับ)
GITHUB_RAW_URL = "https://raw.githubusercontent.com/suriwrrnkulchang-art/55/refs/heads/main/Main.py"

temp_dir = tempfile.gettempdir()
TEMP_FILE = os.path.join(temp_dir, "downloaded_script.py")

try:
    print("กำลังตรวจสอบและดึงไฟล์อัปเดตล่าสุดจาก GitHub...")
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
