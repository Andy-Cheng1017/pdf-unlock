"""解除 PDF 的複製/列印等限制（owner password 保護）。

用法:
  python unlock_pdf.py <檔案或資料夾> [...]   # 資料夾會遞迴處理
  選項: -p 密碼 (需要開啟密碼時)  --backup (另存原檔為 xxx.locked.pdf)
預設直接以解鎖版覆寫原檔，不保留原檔。
"""
import argparse
import os
import sys
from pathlib import Path

import pikepdf


def unlock(path: Path, password: str = "", backup: bool = False) -> str:
    try:
        with pikepdf.open(path, password=password) as pdf:
            if not pdf.is_encrypted:
                return "skip (未加密)"
            tmp = path.with_suffix(".unlocking.tmp")
            pdf.save(tmp)  # 不指定 encryption 即為移除加密
    except pikepdf.PasswordError:
        return "FAIL (需要開啟密碼，請用 -p)"
    except Exception as e:
        return f"FAIL ({e})"
    if backup:
        bak = path.with_name(path.stem + ".locked.pdf")
        if bak.exists():
            bak.unlink()
        os.replace(path, bak)
        os.replace(tmp, path)
    else:
        os.replace(tmp, path)
    return "OK"


def collect(targets):
    for t in targets:
        p = Path(t)
        if p.is_dir():
            for f in p.rglob("*.pdf"):
                if not f.name.lower().endswith(".locked.pdf"):
                    yield f
        elif p.is_file() and p.suffix.lower() == ".pdf":
            yield p


def choose_file():
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        selected = filedialog.askopenfilename(
            title="選擇要解鎖的 PDF",
            filetypes=[("PDF files", "*.pdf")],
        )
        root.destroy()
        return selected
    except Exception as error:
        print(f"無法開啟檔案選擇視窗：{error}", file=sys.stderr)
        return ""


def pause():
    try:
        input("\n按 Enter 關閉...")
    except (EOFError, KeyboardInterrupt):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="*")
    ap.add_argument("-p", "--password", default="")
    ap.add_argument("--backup", action="store_true")
    ap.add_argument("--pause", action="store_true", help="結束前暫停(右鍵選單用)")
    a = ap.parse_args()

    if not a.targets:
        selected = choose_file()
        if not selected:
            print("未選擇 PDF。也可把 PDF 或資料夾拖到 unlock_pdf.exe 上。")
            pause()
            return 1
        a.targets = [selected]

    files = list(collect(a.targets))
    ok = 0
    for f in files:
        r = unlock(f, a.password, a.backup)
        ok += r == "OK"
        print(f"[{r}] {f}")
    print(f"\n完成：{ok}/{len(files)} 個檔案已解鎖")
    if a.pause or not files:
        pause()
    return 0 if files else 1


if __name__ == "__main__":
    sys.exit(main())
