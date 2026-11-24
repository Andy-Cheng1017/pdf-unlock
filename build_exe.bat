@echo off
chcp 65001 >nul
echo 需要 Python 與 pip。正在安裝相依套件並打包 exe...
pip install -r "%~dp0requirements.txt" pyinstaller || exit /b 1
cd /d "%~dp0"
pyinstaller --noconfirm --onedir --console --name unlock_pdf unlock_pdf.py || exit /b 1
echo 完成：dist\unlock_pdf\unlock_pdf.exe（需連同 _internal 資料夾一起使用）
