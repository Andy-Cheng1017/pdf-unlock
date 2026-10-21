# pdf-unlock

批次移除 PDF 的「禁止複製文字 / 列印 / 編輯」限制（owner password 保護），並可加入 Windows 右鍵選單一鍵解鎖。

> ⚠️ 請只用於你有權處理的文件。本工具**無法**破解需要輸入密碼才能開啟的 PDF（除非你提供密碼）。

## 安裝

需要 Python 3.9+（Windows）。

```powershell
git clone https://github.com/<你的帳號>/pdf-unlock.git
cd pdf-unlock
pip install -r requirements.txt
```

## 命令列用法

```powershell
# 解鎖單一檔案
python unlock_pdf.py "C:\path\file.pdf"

# 解鎖整個資料夾（含子資料夾）
python unlock_pdf.py "C:\Users\me\Documents"

# 需要開啟密碼的檔案
python unlock_pdf.py file.pdf -p 密碼

# 另存原檔為 file.locked.pdf（預設不保留原檔，直接覆寫）
python unlock_pdf.py file.pdf --backup
```

> 預設會**直接覆寫原檔**。重要檔案請先備份，或加上 `--backup`。

## Windows 右鍵選單

```powershell
# 安裝（僅目前使用者，不需系統管理員）
powershell -ExecutionPolicy Bypass -File install_context_menu.ps1

# Windows 11：同時改用完整右鍵選單，選項會直接出現，不必按「顯示更多選項」
powershell -ExecutionPolicy Bypass -File install_context_menu.ps1 -ClassicMenu
```

`-ClassicMenu` 會讓整個系統的右鍵選單回到 Win10 樣式，需重新啟動檔案總管（或重新登入）生效。

安裝後，在 PDF 檔案、資料夾，或資料夾空白處按右鍵，選「解鎖 PDF」即可。

### 移除

```powershell
powershell -ExecutionPolicy Bypass -File install_context_menu.ps1 -Uninstall
```

同時會還原 Win11 預設右鍵選單。

## 為什麼 Win11 預設選單需要 `-ClassicMenu`？

Windows 11 的新式頂層選單只允許 MSIX 封裝並簽章的 Shell 擴充，單純的登錄檔項目只會出現在「顯示更多選項」。`-ClassicMenu` 是最簡單、不需簽章的替代方案。

## 授權

MIT
