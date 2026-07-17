@echo off
chcp 65001 >nul
title AI Math School V9 安裝器
echo.
echo ==========================================
echo  AI Math School V9 - GitHub Desktop 安裝器
echo ==========================================
echo.
echo 這個工具會把 V9 網站完整複製到你的 math 專案，
echo 並保留 GitHub Desktop 需要的 .git 資料夾。
echo.
echo 接下來會跳出資料夾選擇視窗。
echo 請選擇 GitHub Desktop 下載的「math」資料夾。
echo.
pause

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$shell = New-Object -ComObject Shell.Application; ^
$f = $shell.BrowseForFolder(0, '請選擇 GitHub Desktop 下載的 math 專案資料夾', 0); ^
if ($null -eq $f) { exit 2 }; ^
$target = $f.Self.Path; ^
$source = Split-Path -Parent '%~f0'; ^
if (-not (Test-Path (Join-Path $target '.git'))) { ^
  Add-Type -AssemblyName PresentationFramework; ^
  [System.Windows.MessageBox]::Show('你選的資料夾不是 GitHub Desktop 下載的 math 專案。請重新執行並選擇正確資料夾。','選錯資料夾','OK','Error') | Out-Null; ^
  exit 3 ^
}; ^
Get-ChildItem -LiteralPath $target -Force | Where-Object { $_.Name -ne '.git' } | Remove-Item -Recurse -Force; ^
Get-ChildItem -LiteralPath $source -Force | Where-Object { $_.Name -notin @('安裝V9到GitHub專案.bat','發布步驟.html') } | Copy-Item -Destination $target -Recurse -Force; ^
Add-Type -AssemblyName PresentationFramework; ^
[System.Windows.MessageBox]::Show('V9 已安裝完成！現在回到 GitHub Desktop，依序按 Commit to main 與 Push origin。','安裝完成','OK','Information') | Out-Null"

if errorlevel 1 (
  echo.
  echo 安裝沒有完成。請確認你選的是 GitHub Desktop 下載的 math 資料夾。
  pause
  exit /b 1
)

echo.
echo 安裝完成。
echo 現在請回到 GitHub Desktop：
echo 1. 左下角按 Commit to main
echo 2. 上方按 Push origin
echo.
pause
