# 安裝右鍵選單（僅目前使用者，不需系統管理員）。移除請加 -Uninstall
# -ClassicMenu：Win11 預設就顯示完整(舊式)右鍵選單，不必再按「顯示更多選項」
param([switch]$Uninstall, [switch]$ClassicMenu)

$clsid = "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
if ($ClassicMenu -and -not $Uninstall) {
    New-Item "$clsid\InprocServer32" -Force | Out-Null
    Set-ItemProperty "$clsid\InprocServer32" -Name "(default)" -Value ""
    Write-Host "已啟用舊式右鍵選單，請重新啟動檔案總管或重新登入後生效"
}
if ($Uninstall) { Remove-Item $clsid -Recurse -Force -ErrorAction SilentlyContinue }

$script = Join-Path $PSScriptRoot "unlock_pdf.py"
$py = (Get-Command python).Source
$keys = @{
    "HKCU:\Software\Classes\SystemFileAssociations\.pdf\shell\UnlockPDF"  = '%1'
    "HKCU:\Software\Classes\Directory\shell\UnlockPDF"                     = '%1'
    "HKCU:\Software\Classes\Directory\Background\shell\UnlockPDF"          = '%V'
}

foreach ($k in $keys.Keys) {
    if ($Uninstall) { Remove-Item $k -Recurse -Force -ErrorAction SilentlyContinue; continue }
    New-Item "$k\command" -Force | Out-Null
    Set-ItemProperty $k -Name "(default)" -Value "解鎖 PDF"
    Set-ItemProperty $k -Name "Icon" -Value "shell32.dll,47"
    $cmd = "`"$py`" `"$script`" --pause `"$($keys[$k])`""
    Set-ItemProperty "$k\command" -Name "(default)" -Value $cmd
}
Write-Host ($(if ($Uninstall) { "已移除右鍵選單" } else { "已安裝右鍵選單" }))
