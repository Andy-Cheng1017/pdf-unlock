"""解除 PDF 的複製/列印等限制（owner password 保護）。

用法:
  python unlock_pdf.py <檔案或資料夾> [...]   # 資料夾會遞迴處理
  選項: -p 密碼 (需要開啟密碼時)  --backup (另存原檔為 xxx.locked.pdf)
預設直接以解鎖版覆寫原檔，不保留原檔。
"""
import argparse
import os
import sys
import tempfile
from pathlib import Path

import pikepdf


def unlock(path: Path, password: str = "", backup: bool = False) -> str:
    try:
        with tempfile.TemporaryDirectory(prefix=".pdf-unlock-", dir=path.parent) as temp_dir:
            tmp = Path(temp_dir) / "unlocked.pdf"
            with pikepdf.open(path, password=password) as pdf:
                if not pdf.is_encrypted:
                    return "skip (未加密)"
                pdf.save(tmp)
            if backup:
                bak = path.with_name(path.stem + ".locked.pdf")
                if bak.exists():
                    return f"FAIL (備份檔已存在：{bak})"
                os.replace(path, bak)
                try:
                    os.replace(tmp, path)
                except OSError:
                    os.replace(bak, path)
                    raise
            else:
                os.replace(tmp, path)
    except pikepdf.PasswordError:
        return "FAIL (需要開啟密碼，請用 -p)"
    except Exception as e:
        return f"FAIL ({e})"
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


def context_menu(installed: bool) -> bool:
    if sys.platform != "win32":
        print("右鍵選單目前僅支援 Windows。", file=sys.stderr)
        return False

    import winreg

    executable = str(Path(sys.executable).resolve())
    command = f'"{executable}"'
    if not getattr(sys, "frozen", False):
        command += f' "{Path(__file__).resolve()}"'
    items = (
        (r"Software\Classes\SystemFileAssociations\.pdf\shell\UnlockPDF", "%1"),
        (r"Software\Classes\Directory\shell\UnlockPDF", "%1"),
        (r"Software\Classes\Directory\Background\shell\UnlockPDF", "%V"),
    )
    if installed:
        for relative_key, argument in items:
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, relative_key) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "解鎖 PDF")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, "shell32.dll,47")
            with winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER, relative_key + r"\command"
            ) as command_key:
                winreg.SetValueEx(
                    command_key,
                    "",
                    0,
                    winreg.REG_SZ,
                    f'{command} --pause "{argument}"',
                )
    else:
        for relative_key, _ in items:
            try:
                winreg.DeleteKeyEx(
                    winreg.HKEY_CURRENT_USER,
                    relative_key + r"\command",
                    access=winreg.KEY_WOW64_64KEY,
                )
                winreg.DeleteKeyEx(
                    winreg.HKEY_CURRENT_USER,
                    relative_key,
                    access=winreg.KEY_WOW64_64KEY,
                )
            except FileNotFoundError:
                pass

    action = "安裝" if installed else "移除"
    print(f"已{action}右鍵選單。")
    if installed:
        print("Windows 11 請在右鍵後按「顯示更多選項」。")
        print(f"程式位置：{command}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="*")
    ap.add_argument("-p", "--password", default="")
    ap.add_argument("--backup", action="store_true")
    ap.add_argument("--pause", action="store_true", help="結束前暫停(右鍵選單用)")
    ap.add_argument("--install-menu", action="store_true", help="安裝 Windows 右鍵選單")
    ap.add_argument(
        "--uninstall-menu", action="store_true", help="移除 Windows 右鍵選單"
    )
    a = ap.parse_args()

    if a.install_menu:
        return 0 if context_menu(True) else 1
    if a.uninstall_menu:
        return 0 if context_menu(False) else 1

    if not a.targets:
        selected = choose_file()
        if not selected:
            print("未選擇 PDF。也可把 PDF 或資料夾拖到 unlock_pdf.exe 上。")
            pause()
            return 1
        a.targets = [selected]

    files = list(collect(a.targets))
    ok = 0
    failed = 0
    for f in files:
        r = unlock(f, a.password, a.backup)
        ok += r == "OK"
        failed += r.startswith("FAIL")
        print(f"[{r}] {f}")
    if not files:
        print("找不到 PDF 檔案，請確認路徑。", file=sys.stderr)
    print(f"\n完成：{ok}/{len(files)} 個檔案已解鎖，{failed} 個失敗")
    if a.pause or getattr(sys, "frozen", False):
        pause()
    return 0 if files and not failed else 1


if __name__ == "__main__":
    sys.exit(main())
