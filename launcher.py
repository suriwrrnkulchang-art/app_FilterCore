#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
 launcher.py — ตัวเรียกโปรแกรมหลัก (Bootstrapper) + ระบบอัพเดทจาก GitHub
=====================================================================
แนวคิด (ง่ายกว่าระบบ Update Channel โฟลเดอร์แชร์แบบเดิมมาก):

  1) เปิดโปรแกรมนี้ (ไฟล์นี้จะถูกคอมไพล์เป็น .exe ไฟล์เดียวด้วย PyInstaller)
  2) เช็คเวอร์ชันล่าสุดจากไฟล์ version.json บน GitHub (ไม่ต้องมีโฟลเดอร์แชร์)
  3) ถ้ามีเวอร์ชันใหม่กว่าที่เครื่องนี้มี -> โชว์ป็อปอัพสไตล์ OBS
     ให้ผู้ใช้เลือก "อัพเดทตอนนี้" หรือ "ภายหลัง"
  4) กด "อัพเดทตอนนี้" -> โหลดไฟล์ Main.py ตัวใหม่จาก GitHub มาเก็บ (แคช)
     ไว้ในเครื่อง แล้วรันไฟล์นั้นทันที
  5) กด "ภายหลัง" หรือไม่มีอัพเดทใหม่ หรือต่อเน็ตไม่ได้ -> รันไฟล์ที่แคช
     ไว้ในเครื่องจากรอบก่อนหน้าแทน (เปิดแบบออฟไลน์ได้)

การเตรียมฝั่ง GitHub (ทำครั้งเดียว แล้วอัพเดตทุกครั้งที่ออกเวอร์ชันใหม่):
  - อัพโหลดไฟล์โปรแกรมหลัก (เช่น Main.py) ขึ้น repo
  - สร้าง/แก้ไฟล์ version.json ให้มีเนื้อหาแบบนี้:

        {
          "version": "1.0.0.012",
          "description": "แก้บั๊ก...\\nเพิ่มฟีเจอร์...",
          "released_at": "2026-07-05",
          "main_url": "https://raw.githubusercontent.com/USER/REPO/main/Main.py"
        }

  - พอผู้ใช้เปิดโปรแกรม launcher.exe รอบถัดไป ระบบจะเจอว่าเวอร์ชันใน
    version.json ใหม่กว่าเวอร์ชันในเครื่อง แล้วเด้งป็อปอัพให้เอง

หมายเหตุสำคัญ: ไฟล์ Main.py ไม่จำเป็นต้อง import auto_updater หรือมี
UPDATE_CHANNEL_DIR อีกต่อไป เพราะ launcher ตัวนี้เป็นคนจัดการอัพเดทให้แล้ว
(ลบส่วนนั้นออกจาก Main.py ได้เลยเพื่อความเรียบร้อย ถึงจะเหลือไว้ก็ไม่พังอะไร
เพราะโค้ดเดิมมี try/except ImportError ครอบไว้อยู่แล้ว)

การคอมไพล์เป็น .exe ไฟล์เดียว (ต้องติดตั้ง pyinstaller ก่อน: pip install pyinstaller):
    pyinstaller --onefile --noconsole --name "SKYFILM Voice Censor" launcher.py

⚠️ ข้อควรระวังด้านความปลอดภัย:
ใครก็ตามที่มีสิทธิ์แก้ไฟล์ในรีโพ GitHub นี้ได้ จะสามารถสั่งให้โค้ดอะไรก็ได้
รันบนเครื่องผู้ใช้ทุกคนที่เปิดโปรแกรมนี้ ดังนั้นควรตั้งรีโพเป็น private หรือ
จำกัดสิทธิ์ผู้ที่ push โค้ดได้ให้รัดกุม
"""

import os
import sys
import json
import tempfile
import traceback
import urllib.request

# --- ⚠️ ต้อง import ทุกโมดูล GUI/ไลบรารีที่โปรแกรมหลัก (Main.py) ใช้ไว้ตรงนี้ ---
# เพื่อให้ PyInstaller รู้และฝัง DLL/ไลบรารีเหล่านี้เข้าไปในไฟล์ .exe ตัวเดียวด้วย
# ตัวที่ import ไว้ตรงนี้ ไม่จำเป็นต้องเรียกใช้งานจริง แค่ import เฉย ๆ ก็พอ
import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog
import tkinter.scrolledtext
import tkinter.font

# 💡 ถ้า Main.py มี import อื่นเพิ่มเติม (เช่นไลบรารีเสียง) ให้เพิ่ม import ตรงนี้ด้วย
# ครอบด้วย try/except กันไว้เผื่อบางเครื่องยังไม่ได้ลงไลบรารีนั้น (ไม่ทำให้ launcher พัง)
try:
    import numpy  # noqa: F401
except ImportError:
    pass
try:
    import pyaudio  # noqa: F401
except ImportError:
    pass
try:
    import speech_recognition  # noqa: F401
except ImportError:
    pass
try:
    import soundfile  # noqa: F401
except ImportError:
    pass


# ============================== ตั้งค่า ==============================
APP_NAME = "SKYFILM Voice Censor"

# TODO: แก้ลิงก์นี้ให้ชี้ไปที่ไฟล์ version.json (raw) บน GitHub repo ของคุณ
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/suriwrrnkulchang-art/55/main/version.json"

# โฟลเดอร์เก็บไฟล์แคช (โค้ดโปรแกรมหลักที่ดาวน์โหลดล่าสุด + เวอร์ชันที่ติดตั้งอยู่ในเครื่อง)
CACHE_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA") or tempfile.gettempdir(),
    "SkyfilmVoiceCensor",
)
CACHED_MAIN_PATH = os.path.join(CACHE_DIR, "main_cached.py")
LOCAL_VERSION_PATH = os.path.join(CACHE_DIR, "version_info.json")

REQUEST_TIMEOUT_SEC = 6


# ============================== ธีมสี (เข้ากับโปรแกรมหลัก) ==============================
TH = {
    "bg": "#101820", "panel": "#182430", "panel_alt": "#1f2e3c",
    "accent": "#3ddc97", "accent_dark": "#25a877",
    "text": "#e7edf3", "text_muted": "#93a2b3",
    "danger": "#ff6b6b", "border": "#2a3947",
}


# ============================== ตัวช่วยจัดการเวอร์ชัน/ไฟล์แคช ==============================
def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def _read_local_version():
    try:
        with open(LOCAL_VERSION_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("version")
    except Exception:
        return None


def _write_local_version(version):
    _ensure_cache_dir()
    with open(LOCAL_VERSION_PATH, "w", encoding="utf-8") as f:
        json.dump({"version": version}, f, ensure_ascii=False, indent=2)


def _version_tuple(v):
    parts = []
    for chunk in str(v).replace("-", ".").replace("_", ".").split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts) if parts else (0,)


def _is_newer(remote_version, local_version):
    if not local_version:
        return True
    try:
        return _version_tuple(remote_version) > _version_tuple(local_version)
    except Exception:
        return str(remote_version) != str(local_version)


def _fetch_json(url):
    with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT_SEC) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_text(url):
    with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT_SEC) as resp:
        return resp.read().decode("utf-8")


def _download_and_cache(main_url, version):
    code = _fetch_text(main_url)
    _ensure_cache_dir()
    with open(CACHED_MAIN_PATH, "w", encoding="utf-8") as f:
        f.write(code)
    _write_local_version(version)


def _run_cached_main():
    """รันโค้ดโปรแกรมหลักจากไฟล์แคชในเครื่อง
    (ใช้ตอนไม่มีอัพเดทใหม่, ผู้ใช้กด 'ภายหลัง', หรือต่อเน็ตไม่ได้)

    หมายเหตุสำคัญ: ต้องใส่ __file__ และ __name__ เข้าไปใน globals ที่ส่งให้ exec()
    ด้วยเสมอ ไม่งั้นโค้ดในไฟล์ที่มีการอ้างอิง __file__ (เช่นหา path ของโปรแกรม
    เพื่อเก็บไฟล์ settings/bad_words หรือหา resource path ตอน build เป็น .exe)
    จะพังด้วย NameError: name '__file__' is not defined ทันที
    """
    with open(CACHED_MAIN_PATH, "r", encoding="utf-8") as f:
        code = f.read()
    exec_globals = {
        "__name__": "__main__",
        "__file__": CACHED_MAIN_PATH,
    }
    exec(compile(code, CACHED_MAIN_PATH, "exec"), exec_globals)


# ============================== ป็อปอัพแจ้งอัพเดท (สไตล์ OBS หน้าเดียว) ==============================
def _show_update_popup(manifest):
    """แสดงป็อปอัพแจ้งอัพเดท คืนค่า 'update' หรือ 'later' ตามที่ผู้ใช้เลือก"""
    import tkinter as tk

    version = manifest.get("version", "-")
    desc = manifest.get("description", "(ไม่มีรายละเอียดเพิ่มเติม)")
    released_at = manifest.get("released_at", "")
    local_ver = _read_local_version() or "(ยังไม่เคยติดตั้ง)"

    root = tk.Tk()
    root.withdraw()  # ไม่ต้องมีหน้าต่างหลักของ launcher โผล่มาให้เกะกะ

    win = tk.Toplevel(root)
    win.title("มีอัพเดทใหม่")
    win.configure(bg=TH["panel"])
    win.resizable(False, False)

    result = {"action": "later"}

    def center():
        win.update_idletasks()
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        ww, wh = win.winfo_width(), win.winfo_height()
        win.geometry(f"+{(sw - ww) // 2}+{(sh - wh) // 2}")

    header = tk.Frame(win, bg=TH["panel"])
    header.pack(fill="x", padx=28, pady=(24, 4))
    tk.Label(header, text="🛡", font=("Segoe UI Emoji", 22), bg=TH["panel"], fg=TH["accent"]).pack(side="left")
    col = tk.Frame(header, bg=TH["panel"])
    col.pack(side="left", padx=(10, 0))
    tk.Label(col, text=f"มีเวอร์ชันใหม่ของ {APP_NAME}", font=("Tahoma", 13, "bold"),
             bg=TH["panel"], fg=TH["text"], anchor="w").pack(anchor="w")
    tk.Label(col, text=f"เวอร์ชัน {version}  (เครื่องนี้ใช้อยู่ {local_ver})",
             bg=TH["panel"], fg=TH["text_muted"], anchor="w").pack(anchor="w")

    tk.Frame(win, bg=TH["border"], height=1).pack(fill="x", padx=28, pady=(14, 0))

    body = tk.Frame(win, bg=TH["panel"])
    body.pack(fill="both", expand=True, padx=28, pady=(14, 0))
    if released_at:
        tk.Label(body, text=f"เผยแพร่เมื่อ: {released_at}", bg=TH["panel"], fg=TH["text_muted"],
                 anchor="w").pack(anchor="w", pady=(0, 8))
    tk.Label(body, text="มีอะไรใหม่บ้าง:", bg=TH["panel"], fg=TH["accent"], anchor="w").pack(anchor="w")
    box = tk.Text(body, width=54, height=8, wrap="word", bg=TH["panel_alt"], fg=TH["text"],
                  relief="flat", borderwidth=0, padx=10, pady=8)
    box.insert("1.0", desc)
    box.config(state="disabled")
    box.pack(fill="both", expand=True, pady=(6, 0))

    footer = tk.Frame(win, bg=TH["panel"])
    footer.pack(fill="x", padx=28, pady=(14, 22))

    def choose_later():
        result["action"] = "later"
        win.destroy()
        root.quit()

    def choose_update():
        result["action"] = "update"
        win.destroy()
        root.quit()

    tk.Button(footer, text="ภายหลัง", command=choose_later, bg=TH["panel_alt"], fg=TH["text"],
              relief="flat", padx=20, pady=8).pack(side="right", padx=(8, 0))
    tk.Button(footer, text="⬇  อัพเดทตอนนี้", command=choose_update, bg=TH["accent"], fg="#062018",
              relief="flat", padx=22, pady=8, font=("Tahoma", 10, "bold")).pack(side="right")

    win.protocol("WM_DELETE_WINDOW", choose_later)
    center()
    root.mainloop()
    try:
        root.destroy()
    except Exception:
        pass

    return result["action"]


def _show_downloading_popup_and_run(main_url, version):
    """โชว์หน้ากำลังดาวน์โหลด/ติดตั้ง แล้วรันโปรแกรมหลักเมื่อเสร็จ (หรือแจ้ง error)"""
    import tkinter as tk
    from tkinter import ttk
    import threading

    root = tk.Tk()
    root.withdraw()
    win = tk.Toplevel(root)
    win.title("กำลังอัพเดท")
    win.configure(bg=TH["panel"])
    win.resizable(False, False)
    win.protocol("WM_DELETE_WINDOW", lambda: None)  # กันปิดระหว่างติดตั้ง

    tk.Label(win, text="⏳ กำลังดาวน์โหลดและติดตั้งอัพเดท กรุณารอสักครู่...",
             bg=TH["panel"], fg=TH["text"], font=("Tahoma", 11)).pack(padx=32, pady=(28, 12))
    progress = ttk.Progressbar(win, mode="indeterminate", length=320)
    progress.pack(padx=32, pady=(0, 28))
    progress.start(12)

    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    ww, wh = win.winfo_width(), win.winfo_height()
    win.geometry(f"+{(sw - ww) // 2}+{(sh - wh) // 2}")

    state = {"ok": None, "err": None}

    def do_download():
        try:
            _download_and_cache(main_url, version)
            state["ok"] = True
        except Exception as e:
            state["ok"] = False
            state["err"] = str(e)
        root.quit()

    threading.Thread(target=do_download, daemon=True).start()
    root.mainloop()
    try:
        win.destroy()
        root.destroy()
    except Exception:
        pass

    if not state["ok"]:
        _show_error_popup(f"อัพเดทไม่สำเร็จ: {state['err']}\nจะเปิดโปรแกรมเวอร์ชันเดิมที่มีอยู่แทน")


def _show_error_popup(message):
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    win = tk.Toplevel(root)
    win.title("เกิดข้อผิดพลาด")
    win.configure(bg=TH["panel"])
    win.resizable(False, False)
    tk.Label(win, text="❌ " + message, bg=TH["panel"], fg=TH["danger"], padx=24, pady=20,
             wraplength=380, justify="left").pack()
    tk.Button(win, text="ปิด", command=lambda: (win.destroy(), root.quit()),
              bg=TH["panel_alt"], fg=TH["text"], relief="flat", padx=20, pady=6).pack(pady=(0, 18))
    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), root.quit()))
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    ww, wh = win.winfo_width(), win.winfo_height()
    win.geometry(f"+{(sw - ww) // 2}+{(sh - wh) // 2}")
    root.mainloop()
    try:
        root.destroy()
    except Exception:
        pass


# ============================== main ==============================
def main():
    _ensure_cache_dir()
    have_cache = os.path.exists(CACHED_MAIN_PATH)

    try:
        manifest = _fetch_json(GITHUB_VERSION_URL)
        remote_version = manifest.get("version")
        main_url = manifest.get("main_url")
        if not remote_version or not main_url:
            raise ValueError("version.json ไม่มีข้อมูล version หรือ main_url ครบถ้วน")
    except Exception:
        # ต่อเน็ตไม่ได้ / GitHub ล่ม / version.json มีปัญหา
        if have_cache:
            _run_cached_main()
            return
        _show_error_popup(
            "เชื่อมต่ออินเทอร์เน็ตไม่ได้ หรือดึงข้อมูลเวอร์ชันจาก GitHub ไม่สำเร็จ "
            "และยังไม่เคยดาวน์โหลดโปรแกรมมาก่อนในเครื่องนี้\n\n"
            "กรุณาเชื่อมต่ออินเทอร์เน็ตแล้วเปิดโปรแกรมใหม่อีกครั้ง"
        )
        return

    local_version = _read_local_version()

    if not have_cache:
        # เปิดเครื่องนี้เป็นครั้งแรก ยังไม่เคยมีโปรแกรมอยู่เลย -> ดาวน์โหลดทันทีแบบเงียบ ๆ ไม่ต้องถาม
        try:
            _download_and_cache(main_url, remote_version)
        except Exception as e:
            _show_error_popup(f"ดาวน์โหลดโปรแกรมไม่สำเร็จ: {e}")
            return
        _run_cached_main()
        return

    if _is_newer(remote_version, local_version):
        action = _show_update_popup(manifest)
        if action == "update":
            _show_downloading_popup_and_run(main_url, remote_version)
        # ไม่ว่าอัพเดทสำเร็จ ล้มเหลว หรือกด 'ภายหลัง' ก็ตาม ให้รันไฟล์แคชล่าสุดที่มีอยู่เสมอ
        _run_cached_main()
    else:
        _run_cached_main()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        try:
            _show_error_popup("เกิดข้อผิดพลาดที่ไม่คาดคิด: " + traceback.format_exc()[-300:])
        except Exception:
            input("เกิดข้อผิดพลาด กด Enter เพื่อปิด...")
