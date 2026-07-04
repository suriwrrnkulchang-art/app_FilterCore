import urllib.request
import subprocess
import os
import sys

# ⚠️ เอาลิงก์ Raw URL ที่ก๊อปมาจากข้อ 1 มาวางตรงนี้แทนที่ลิงก์ตัวอย่างนะครับ
GITHUB_RAW_URL = "https://raw.githubusercontent.com/suriwrrnkulchang-art/55/refs/heads/main/Main.py"
TEMP_FILE = "running_app.py"

try:
    print("กำลังตรวจสอบการอัปเดตจาก GitHub...")
    # ดาวน์โหลดโค้ดเวอร์ชันล่าสุดจาก GitHub มาเก็บไว้ชั่วคราว
    urllib.request.urlretrieve(GITHUB_RAW_URL, TEMP_FILE)
    
    # สั่งรันโค้ดตัดคำที่เพิ่งดาวน์โหลดมาทันที
    subprocess.run([sys.executable, TEMP_FILE])
    
except Exception as e:
    print(f"ไม่สามารถเชื่อมต่อ GitHub หรือเกิดข้อผิดพลาด: {e}")
    input("กด Enter เพื่อปิดโปรแกรม...")
finally:
    # เมื่อปิดโปรแกรมตัดคำ ให้ลบไฟล์ชั่วคราวทิ้งทันทีเพื่อไม่ให้รกเครื่องคนใช้งาน
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)
