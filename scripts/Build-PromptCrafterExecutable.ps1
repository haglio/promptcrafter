$ErrorActionPreference = 'Stop'

$LauncherRoot = Split-Path -Parent $PSScriptRoot
$NodeExe = 'C:\Program Files\nodejs\npm.cmd'
$IconGenerator = Join-Path $LauncherRoot 'scripts\Generate-PromptCrafterIcon.py'
$PackageOutputRoot = Join-Path $LauncherRoot 'build\electron'
$PackagedFolder = Join-Path $PackageOutputRoot 'PromptCrafter-win32-x64'
$RuntimeRoot = Join-Path $LauncherRoot 'PromptCrafter-runtime'
$LegacyExe = Join-Path $LauncherRoot 'PromptCrafter.exe'
$LegacyInternal = Join-Path $LauncherRoot '_internal'
$PackagerCli = Join-Path $LauncherRoot 'node_modules\@electron\packager\bin\electron-packager.mjs'

if (-not (Test-Path -LiteralPath $IconGenerator)) {
  throw "Icon generator was not found at $IconGenerator"
}

if (-not (Test-Path -LiteralPath $PackagerCli)) {
  throw "Electron packager CLI was not found at $PackagerCli"
}

Push-Location $LauncherRoot
try {
  $running = Get-Process -Name 'PromptCrafter' -ErrorAction SilentlyContinue
  if ($running) {
    Stop-Process -Id $running.Id -Force
    Start-Sleep -Milliseconds 500
  }

  Remove-Item -LiteralPath $LegacyExe -Force -ErrorAction SilentlyContinue
  if (Test-Path -LiteralPath $LegacyInternal) {
    Remove-Item -LiteralPath $LegacyInternal -Recurse -Force
  }

  & 'C:\Windows\py.exe' -3 $IconGenerator
  if ($LASTEXITCODE -ne 0) {
    throw "Icon generation failed with exit code $LASTEXITCODE"
  }

  & $NodeExe run build
  if ($LASTEXITCODE -ne 0) {
    throw "Frontend build failed with exit code $LASTEXITCODE"
  }

  if (Test-Path -LiteralPath $PackageOutputRoot) {
    Remove-Item -LiteralPath $PackageOutputRoot -Recurse -Force
  }

  & 'C:\Program Files\nodejs\node.exe' $PackagerCli `
    . `
    PromptCrafter `
    --platform=win32 `
    --arch=x64 `
    --out=$PackageOutputRoot `
    --overwrite `
    --prune=true `
    --icon="$LauncherRoot\icon.ico" `
    --executable-name=PromptCrafter `
    --app-version=0.0.1 `
    --app-copyright='Alex' `
    --win32metadata.ProductName='PromptCrafter' `
    --win32metadata.FileDescription='PromptCrafter Desktop App' `
    --ignore='^/build($|/)' `
    --ignore='^/tests($|/)' `
    --ignore='^/src($|/)' `
    --ignore='^/promptcrafter-.*\.log$' `
    --ignore='^/PromptCrafter-runtime($|/)' `
    --ignore='^/PromptCrafter\.lnk$'

  if ($LASTEXITCODE -ne 0) {
    throw "Electron packaging failed with exit code $LASTEXITCODE"
  }

  if (-not (Test-Path -LiteralPath $PackagedFolder)) {
    throw "Packaged app folder was not found at $PackagedFolder"
  }

  if (Test-Path -LiteralPath $RuntimeRoot) {
    Remove-Item -LiteralPath $RuntimeRoot -Recurse -Force
  }

  Copy-Item -LiteralPath $PackagedFolder -Destination $RuntimeRoot -Recurse -Force
}
finally {
  Pop-Location
}

Write-Host "Built runtime: $RuntimeRoot"
Write-Host "Executable: $(Join-Path $RuntimeRoot 'PromptCrafter.exe')"
