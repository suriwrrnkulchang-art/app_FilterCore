import urllib.request
import subprocess
import os
import sys
import tempfile

# ⚠️ ลบลิงก์ข้างล่างนี้ออก แล้ววางลิงก์ Raw URL ที่คุณก๊อปมาจากขั้นตอนที่ 1 ลงไปแทนครับ
GITHUB_RAW_URL = "https://raw.githubusercontent.com/suriwrrnkulchang-art/55/refs/heads/main/Main.py"

temp_dir = tempfile.gettempdir()
# เปลี่ยนชื่อไฟล์ดาวน์โหลดเพื่อไม่ให้ซ้ำซ้อนและป้องกันการเกิดลูปนรก
TEMP_FILE = os.path.join(temp_dir, "downloaded_runner.py")

try:
    print("กำลังตรวจสอบการอัปเดตจาก GitHub...")
    # ดาวน์โหลดไฟล์ลง Temp ของ Windows เพื่อแก้ปัญหา Permission Denied
    urllib.request.urlretrieve(GITHUB_RAW_URL, TEMP_FILE)
    
    print("กำลังเรียกใช้งานโปรแกรม...")
    # สั่งรันไฟล์ที่เพิ่งโหลดมาด้วย Python
    subprocess.run([sys.executable, TEMP_FILE])
    
except Exception as e:
    print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
    input("กด Enter เพื่อปิดโปรแกรม...")
finally:
    # ลบไฟล์ชั่วคราวทิ้งทันทีเมื่อปิดโปรแกรม
    if os.path.exists(TEMP_FILE):
        try:
            os.remove(TEMP_FILE)
        except:
            pass
