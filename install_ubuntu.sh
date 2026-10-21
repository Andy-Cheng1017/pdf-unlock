#!/usr/bin/env bash
# Ubuntu 安裝/移除「解鎖 PDF」右鍵選單（Nautilus 檔案管理員，僅目前使用者）
# 用法: ./install_ubuntu.sh          安裝
#       ./install_ubuntu.sh --uninstall   移除
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL="$HOME/.local/share/pdf-unlock"
SCRIPTS="$HOME/.local/share/nautilus/scripts"
NAME="解鎖 PDF"

if [ "$1" = "--uninstall" ]; then
    rm -rf "$INSTALL" "$SCRIPTS/$NAME"
    echo "已移除"
    exit 0
fi

sudo apt-get update -qq
sudo apt-get install -y python3 python3-venv libnotify-bin

mkdir -p "$INSTALL" "$SCRIPTS"
python3 -m venv "$INSTALL/venv"
"$INSTALL/venv/bin/pip" install -q -r "$DIR/requirements.txt"
cp "$DIR/unlock_pdf.py" "$INSTALL/"

cat > "$SCRIPTS/$NAME" <<EOF
#!/usr/bin/env bash
# Nautilus 會把選取的檔案/資料夾放在 NAUTILUS_SCRIPT_SELECTED_FILE_PATHS；
# 在資料夾空白處執行時則用目前資料夾
if [ -n "\$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS" ]; then
    mapfile -t T <<< "\$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS"
else
    T=("\$PWD")
fi
OUT=\$("$INSTALL/venv/bin/python" "$INSTALL/unlock_pdf.py" "\${T[@]}" 2>&1 | tail -n 1)
notify-send "解鎖 PDF" "\$OUT" 2>/dev/null || echo "\$OUT"
EOF
chmod +x "$SCRIPTS/$NAME"
echo "已安裝。請在檔案管理員對 PDF 或資料夾按右鍵 → 「Scripts」→「$NAME」"
echo "若看不到，請執行: nautilus -q  後重新開啟檔案管理員"
