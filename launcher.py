import urllib.request
import os
import tempfile

# 1. เอาลิงก์ Raw URL ของไฟล์ที่คุณต้องการให้มันโหลดมารัน มาวางตรงนี้ครับ
GITHUB_RAW_URL = "https://raw.githubusercontent.com/suriwrrnkulchang-art/55/refs/heads/main/Main.py"

# 2. บันทึกไฟล์ในโฟลเดอร์ Temp ของ Windows เพื่อไม่ให้ติดปัญหา Permission Denied
temp_dir = tempfile.gettempdir()
TEMP_FILE = os.path.join(temp_dir, "downloaded_script.py")

try:
    print("กำลังตรวจสอบและดึงไฟล์อัปเดตล่าสุดจาก GitHub...")
    urllib.request.urlretrieve(GITHUB_RAW_URL, TEMP_FILE)
    
    print("กำลังเริ่มทำงาน...")
    # 💡 หัวใจสำคัญที่แก้ลูปนรก: อ่านโค้ดที่โหลดมาแล้วรันในตัวโปรแกรม .exe เดิมทันที
    # จะไม่มีการเปิด .exe ซ้อนกัน ไม่เกิดลูปนรก 100% ครับ!
    with open(TEMP_FILE, "r", encoding="utf-8") as f:
        downloaded_code = f.read()
    
    exec(downloaded_code, globals())
    
except Exception as e:
    print(f"เกิดข้อผิดพลาดในการรันระบบ: {e}")
    input("กด Enter เพื่อปิดโปรแกรม...")
finally:
    # เมื่อโปรแกรมทำงานเสร็จหรือปิดลง ให้ลบไฟล์ชั่วคราวทิ้งทันที
    if os.path.exists(TEMP_FILE):
        try:
            os.remove(TEMP_FILE)
        except:
            pass
