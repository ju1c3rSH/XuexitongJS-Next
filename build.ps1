param(
    [switch]$Clean,
    [switch]$Debug
)

$ErrorActionPreference = "Stop"

if ($Clean -and (Test-Path "dist")) {
    Write-Host "清理旧构建..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "dist", "build" -ErrorAction SilentlyContinue
    Get-Item "*.spec" -Exclude "build.spec" -ErrorAction SilentlyContinue | Remove-Item -Force
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "data/log/build_$timestamp.log"

if (-not (Test-Path "data/log")) {
    New-Item -ItemType Directory -Path "data/log" -Force | Out-Null
}

Write-Host "正在打包 uXuexitong..." -ForegroundColor Cyan
Write-Host "日志: $logFile" -ForegroundColor DarkGray

$specArgs = @(
    "build.spec"
)

if ($Debug) {
    $specArgs += "--debug", "all"
}

pyinstaller @specArgs 2>&1 | Tee-Object -FilePath $logFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n打包成功！" -ForegroundColor Green
    Write-Host "输出目录: $([System.IO.Path]::GetFullPath('dist/uXuexitong/'))" -ForegroundColor Green
    Write-Host "运行: .\dist\uXuexitong\uXuexitong.exe" -ForegroundColor Green
} else {
    Write-Host "`n打包失败，详情请查看日志: $logFile" -ForegroundColor Red
    exit 1
}
