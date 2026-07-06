"""
updater.py — ตัวเช็คอัปเดตสำหรับแอปหลัก (ปลอดภัย: เช็คเวอร์ชัน + ตรวจ checksum ก่อนใช้เสมอ)
================================================================================
ต่างจากแบบเดิม (โหลดไฟล์ .py จาก URL แล้ว exec ทันที) ตรงนี้:
  1) เช็คจาก "GitHub Releases" (เวอร์ชันที่ปล่อยจริง มี tag ชัดเจน)
     ไม่ใช่ไฟล์ล่าสุดบน branch main ที่เปลี่ยนได้ตลอดเวลาโดยไม่รู้ตัว
  2) ดาวน์โหลดเป็น "ไฟล์ zip ของซอร์สโค้ด" มาแตกทับไฟล์เดิม
     ไม่ใช่การ exec() ข้อความที่โหลดมาสด ๆ (ซึ่งอันตรายมาก เพราะรันได้ทุกอย่าง
     โดยไม่มีการตรวจสอบใดๆก่อนเลย)
  3) *สำคัญที่สุด* ต้องตรวจ SHA-256 checksum ของไฟล์ที่โหลดมา เทียบกับ
     checksums.txt ที่แนบมาในชุด release เดียวกันก่อนเสมอ
     ถ้าค่าไม่ตรง = ปฏิเสธการอัปเดต ไม่แตะไฟล์เดิมแม้แต่ไฟล์เดียว
  4) เก็บเวอร์ชันปัจจุบันไว้ในไฟล์ version.txt ในโฟลเดอร์ติดตั้ง
     เทียบกับ tag ล่าสุดจาก GitHub ก่อนตัดสินใจว่าจะอัปเดตหรือไม่

วิธีใช้:
  ในโปรแกรมหลักของคุณ (main.py) ให้เรียกใช้ตอนเริ่มโปรแกรม เช่น:

      from updater import check_for_update
      check_for_update()   # เช็คแล้วถ้ามีเวอร์ชันใหม่ + checksum ตรง จะอัปเดตให้อัตโนมัติ

ตั้งค่า GITHUB_OWNER / GITHUB_REPO / ASSET_ZIP_NAME ให้ตรงกับ repo จริงของคุณด้านล่าง
"""

import os
import sys
import json
import hashlib
import shutil
import zipfile
import tempfile
import subprocess
import urllib.request
import urllib.error

# ------------------------------------------------------------------
# ตั้งค่าตรงนี้ให้ตรงกับ repo และไฟล์ release ของคุณ
# ------------------------------------------------------------------
GITHUB_OWNER = "suriwrrnkulchang-art"
GITHUB_REPO = "55"                      # ชื่อ repo (ไม่ใช่ branch)
ASSET_ZIP_NAME = "FilterCore-source.zip"     # ชื่อไฟล์ zip ซอร์สโค้ดที่แนบใน release
CHECKSUM_ASSET_NAME = "checksums.txt"        # ไฟล์รวม sha256 ที่แนบใน release เดียวกัน

# โฟลเดอร์ที่แอปติดตั้งอยู่ (ไฟล์นี้ควรอยู่ในโฟลเดอร์เดียวกับ main.py)
INSTALL_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(INSTALL_DIR, "version.txt")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36"
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


# ==================================================================
# ฟังก์ชันช่วยเหลือ
# ==================================================================

def _http_get_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _download(url, dest_path):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp, open(dest_path, "wb") as f:
        shutil.copyfileobj(resp, f)


def _sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def get_local_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "0.0.0"


def set_local_version(tag):
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(tag.strip())


def get_latest_release():
    """คืนค่า dict ของ release ล่าสุดจาก GitHub API (มี tag_name และ assets)"""
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
    return _http_get_json(url)


def _find_asset_url(release, asset_name):
    for asset in release.get("assets", []):
        if asset.get("name") == asset_name:
            return asset.get("browser_download_url")
    return None


def _expected_hash_from_checksums(checksums_text, target_filename):
    """checksums.txt เป็นรูปแบบมาตรฐาน: '<sha256>  <ชื่อไฟล์>' ต่อบรรทัด"""
    for line in checksums_text.splitlines():
        parts = line.strip().split()
        if len(parts) == 2 and parts[1] == target_filename:
            return parts[0].lower()
    return None


# ==================================================================
# ฟังก์ชันหลัก: เช็คและอัปเดต
# ==================================================================

def check_for_update(auto_restart=True):
    """
    เช็คว่ามีเวอร์ชันใหม่กว่าบนเครื่องหรือไม่ ถ้ามี + checksum ตรง จะอัปเดตให้อัตโนมัติ
    คืนค่า True ถ้าอัปเดตสำเร็จ, False ถ้าไม่มีอัปเดตหรือเช็คไม่สำเร็จ (เช่น ไม่มีเน็ต)
    ถ้า checksum ไม่ตรง จะ raise RuntimeError (ไม่แตะไฟล์เดิมเลย)
    """
    try:
        release = get_latest_release()
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return False  # เน็ตมีปัญหา หรือ GitHub เข้าไม่ได้ -> ไม่อัปเดต ไม่ล้มโปรแกรม

    latest_tag = release.get("tag_name", "")
    local_version = get_local_version()
    if not latest_tag or latest_tag == local_version:
        return False  # ไม่มีเวอร์ชันใหม่

    zip_url = _find_asset_url(release, ASSET_ZIP_NAME)
    checksum_url = _find_asset_url(release, CHECKSUM_ASSET_NAME)
    if not zip_url or not checksum_url:
        return False  # release นี้ไม่มีไฟล์ที่ต้องการ ข้ามไปก่อน

    tmp_dir = tempfile.mkdtemp(prefix="update_")
    zip_path = os.path.join(tmp_dir, ASSET_ZIP_NAME)
    checksum_path = os.path.join(tmp_dir, CHECKSUM_ASSET_NAME)

    try:
        _download(zip_url, zip_path)
        _download(checksum_url, checksum_path)

        with open(checksum_path, "r", encoding="utf-8") as f:
            checksums_text = f.read()

        expected_hash = _expected_hash_from_checksums(checksums_text, ASSET_ZIP_NAME)
        if not expected_hash:
            raise RuntimeError(f"ไม่พบ checksum ของ {ASSET_ZIP_NAME} ใน checksums.txt — ปฏิเสธการอัปเดต")

        actual_hash = _sha256_of_file(zip_path)
        if actual_hash.lower() != expected_hash:
            raise RuntimeError(
                "checksum ไม่ตรงกัน! ไฟล์อัปเดตอาจถูกแก้ไข/เสียหาย — ปฏิเสธการอัปเดตเพื่อความปลอดภัย"
            )

        if not zipfile.is_zipfile(zip_path):
            raise RuntimeError("ไฟล์ที่โหลดมาไม่ใช่ zip ที่ถูกต้อง — ปฏิเสธการอัปเดต")

        # checksum ตรง -> ปลอดภัยพอที่จะแตกไฟล์ทับของเดิม
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(INSTALL_DIR)

        set_local_version(latest_tag)

        if auto_restart:
            _restart_main_app()

        return True

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _restart_main_app():
    """เปิด main.py ตัวใหม่ (หลังอัปเดต) แล้วปิดตัวปัจจุบัน"""
    main_file = os.path.join(INSTALL_DIR, "main.py")
    if not os.path.exists(main_file):
        return
    python_exe = sys.executable
    folder = os.path.dirname(python_exe)
    pythonw_exe = os.path.join(folder, "pythonw.exe")
    exe_to_run = pythonw_exe if os.path.exists(pythonw_exe) else python_exe

    clean_env = os.environ.copy()
    clean_env.pop("TCL_LIBRARY", None)
    clean_env.pop("TK_LIBRARY", None)
    clean_env.pop("PYTHONHOME", None)

    subprocess.Popen(
        [exe_to_run, main_file], cwd=INSTALL_DIR,
        creationflags=CREATE_NO_WINDOW, env=clean_env,
    )
    sys.exit(0)


if __name__ == "__main__":
    updated = check_for_update(auto_restart=False)
    print("มีการอัปเดตและติดตั้งเรียบร้อย" if updated else "ไม่มีเวอร์ชันใหม่ หรือเช็คไม่สำเร็จ")
