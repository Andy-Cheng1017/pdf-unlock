@echo off
if not exist "%~dp0unlock_pdf.exe" (
  echo [錯誤] 找不到 unlock_pdf.exe。
  echo 這份檔案不是 Windows 安裝包，請到 GitHub Releases 下載 pdf-unlock-win.zip。
  pause
  exit /b 1
)
"%~dp0unlock_pdf.exe" --install-menu
if errorlevel 1 (
  echo [錯誤] 安裝失敗，請保留以上訊息聯絡維護者。
  pause
  exit /b 1
)
pause
