# pdf-unlock

批次移除 PDF 的「禁止複製文字 / 列印 / 編輯」限制（owner password 保護），並可加入 Windows 右鍵選單一鍵解鎖。

- ✅ 免安裝 Python（提供單一 exe）
- ✅ 可解鎖單一檔案或整個資料夾（含子資料夾）
- ✅ Windows 右鍵一鍵解鎖，不改動 Win11 預設右鍵選單
- ⚠️ 預設**直接覆寫原檔**（加 `--backup` 可保留舊檔）

> 請只用於你有權處理的文件。本工具**無法**破解需要輸入密碼才能「開啟」的 PDF（除非你提供密碼）。

---

## 方法 A：一般使用者（不需要 Python）

### 1. 下載
到 [Releases](../../releases/latest) 的 **Assets** 下載 `pdf-unlock-win.zip`。

> 不要下載「Source code」。Source code 是給開發者用的，沒有 `unlock_pdf.exe`。

### 2. 解壓縮到「固定」位置
例如 `C:\Tools\pdf-unlock\`。
**不要放在下載資料夾或桌面**，右鍵選單會記住這個路徑，檔案搬走就失效。

解壓後資料夾內容：

```
unlock_pdf.exe
install.bat
uninstall.bat
install_context_menu.ps1
```

> 若 Windows SmartScreen 出現「已保護您的電腦」，點「其他資訊」→「仍要執行」。exe 未簽章，這是正常現象。

### 3. 安裝右鍵選單
雙擊 `install.bat`，看到「已安裝右鍵選單」即完成（不需系統管理員）。

### 4. 使用
- **單一 PDF**：對 PDF 按右鍵 →（Windows 11 需先點 **顯示更多選項**）→ **解鎖 PDF**
- **整個資料夾**：對資料夾按右鍵 → **解鎖 PDF**；或在資料夾內的空白處按右鍵 → **解鎖 PDF**
- **拖曳**：把 PDF 或資料夾直接拖到 `unlock_pdf.exe` 上

跑完會顯示 `[OK]` 與成功數量。`[skip]` 表示該檔本來就沒有加密。

> 關於 Windows 11：新式右鍵選單只允許簽章的 MSIX 擴充，一般登錄檔項目只會出現在「顯示更多選項」，因此本工具不更動系統預設選單。想一直顯示完整選單，可自行參考網路上的「Win11 還原舊式右鍵選單」設定，與本工具無關。

### 5. 移除
雙擊 `uninstall.bat`，再刪除資料夾即可。

---

## 方法 B：用 Python（開發者）

需要 Python 3.9+。

```powershell
git clone https://github.com/Andy-Cheng1017/pdf-unlock.git
cd pdf-unlock
pip install -r requirements.txt

python unlock_pdf.py "C:\path\file.pdf"          # 單一檔案
python unlock_pdf.py "C:\Users\me\Documents"     # 整個資料夾（遞迴）
python unlock_pdf.py file.pdf -p 密碼             # 需要開啟密碼
python unlock_pdf.py file.pdf --backup           # 另存原檔為 file.locked.pdf
```

安裝右鍵選單（沒有 exe 時會自動改用 `python unlock_pdf.py`）：

```powershell
powershell -ExecutionPolicy Bypass -File install_context_menu.ps1
powershell -ExecutionPolicy Bypass -File install_context_menu.ps1 -Uninstall
```

### 自行打包 exe

```powershell
build_exe.bat      # 產生 dist\unlock_pdf.exe
```

---

## Ubuntu（Nautilus 檔案管理員）

```bash
sudo apt install -y git
git clone https://github.com/Andy-Cheng1017/pdf-unlock.git
cd pdf-unlock
bash install_ubuntu.sh
```

腳本會自動安裝 Python 環境與 pikepdf（放在 `~/.local/share/pdf-unlock`，不需另外裝 Python 套件）。

使用：在檔案管理員對 PDF、資料夾或資料夾空白處按右鍵 → **Scripts（腳本）→ 解鎖 PDF**，完成後會跳出通知。若選單沒出現，執行 `nautilus -q` 後重新開啟。

命令列也可使用：`~/.local/share/pdf-unlock/venv/bin/python ~/.local/share/pdf-unlock/unlock_pdf.py <檔案或資料夾>`

移除：`bash install_ubuntu.sh --uninstall`

> Ubuntu 的 Nautilus 把自訂項目收在「Scripts」子選單，無法放到頂層。

---

## 常見問題

| 問題 | 解法 |
|------|------|
| 顯示 `FAIL (需要開啟密碼…)` | 這類 PDF 開啟就要密碼，改用 `-p 密碼`（命令列） |
| 右鍵選單沒出現 | Win11 請點「顯示更多選項」；或重新執行 `install.bat` |
| 執行 `install.bat` 顯示找不到 exe | 你下載了 Source code；請重新下載 Releases 的 `pdf-unlock-win.zip` |
| 搬動資料夾後右鍵失效 | 在新位置重新執行 `install.bat` |
| 解鎖後仍無法複製文字 | 該 PDF 可能是掃描圖片，沒有文字層，需要 OCR |
| 想保留原檔 | 命令列加 `--backup` |

## 運作原理

使用 [pikepdf](https://github.com/pikepdf/pikepdf)（qpdf）讀取 PDF 後，以不加密方式重新存檔，移除 owner password 設定的使用限制。

## 授權

MIT
