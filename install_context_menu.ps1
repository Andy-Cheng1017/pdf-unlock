# 安裝/移除「解鎖 PDF」右鍵選單（僅目前使用者，不需系統管理員）
# 若同資料夾有 unlock_pdf.exe 就用它（不需 Python），否則使用 python unlock_pdf.py
param([switch]$Uninstall)

$exe = Join-Path $PSScriptRoot "unlock_pdf.exe"
$py  = Join-Path $PSScriptRoot "unlock_pdf.py"
if (Test-Path $exe) {
    $prefix = "`"$exe`""
} elseif (Test-Path $py) {
    $python = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $python) { Write-Host "找不到 unlock_pdf.exe 或 Python"; exit 1 }
    $prefix = "`"$python`" `"$py`""
} else {
    Write-Host "找不到 unlock_pdf.exe 或 unlock_pdf.py"; exit 1
}

if (-not (Test-Path $exe)) {
    if (-not (Test-Path $py) -or -not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "這是原始碼，不是 Windows 安裝包。請至 GitHub Releases 下載 pdf-unlock-win.zip。"
        exit 1
    }
    Write-Host "警告：目前使用 Python 版本。一般使用者請改用 Releases 的免安裝 zip。" -ForegroundColor Yellow
}

$keys = @{
    "HKCU:\Software\Classes\SystemFileAssociations\.pdf\shell\UnlockPDF" = '%1'
    "HKCU:\Software\Classes\Directory\shell\UnlockPDF"                    = '%1'
    "HKCU:\Software\Classes\Directory\Background\shell\UnlockPDF"         = '%V'
}

foreach ($k in $keys.Keys) {
    if ($Uninstall) { Remove-Item $k -Recurse -Force -ErrorAction SilentlyContinue; continue }
    New-Item "$k\command" -Force | Out-Null
    Set-ItemProperty $k -Name "(default)" -Value "解鎖 PDF"
    Set-ItemProperty $k -Name "Icon" -Value "shell32.dll,47"
    Set-ItemProperty "$k\command" -Name "(default)" -Value "$prefix --pause `"$($keys[$k])`""
}
Write-Host ($(if ($Uninstall) { "已移除右鍵選單" } else { "已安裝右鍵選單（Win11 請在右鍵後按「顯示更多選項」）" }))
