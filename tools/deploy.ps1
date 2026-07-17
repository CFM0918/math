$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "`nAI Math School V8 一鍵發布" -ForegroundColor Yellow
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "找不到 Git。請先安裝 Git for Windows。" }
if (-not (Test-Path '.git')) { throw "此資料夾尚未連接 GitHub。請先依 README 執行首次設定：把 V8 檔案複製到已 clone 的 math 資料夾。" }
if (Get-Command python -ErrorAction SilentlyContinue) {
  python tools/check_links.py
  if ($LASTEXITCODE -ne 0) { throw "連結檢查失敗，已停止發布。" }
} else { Write-Host "未安裝 Python，略過連結檢查。" -ForegroundColor DarkYellow }
$branch=(git branch --show-current).Trim(); if (-not $branch) { $branch='main'; git branch -M main }
Write-Host "同步 GitHub 最新版本..." -ForegroundColor Cyan
git pull --rebase --autostash origin $branch
if ($LASTEXITCODE -ne 0) { throw "同步失敗，請處理 Git 衝突後再試。" }
git add -A
$changes=git status --porcelain
if (-not $changes) { Write-Host "沒有新變更，不需要發布。" -ForegroundColor Green; exit 0 }
$stamp=Get-Date -Format 'yyyy-MM-dd HH:mm'
git commit -m "Update AI Math School V8 $stamp"
if ($LASTEXITCODE -ne 0) { throw "Git commit 失敗。" }
git push origin $branch
if ($LASTEXITCODE -ne 0) { throw "Git push 失敗。" }
Write-Host "`n發布成功！GitHub Pages 通常需要 1～3 分鐘更新。" -ForegroundColor Green
Write-Host "網站：https://cfm0918.github.io/math/" -ForegroundColor Yellow
