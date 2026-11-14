param([switch]$Release)
$ErrorActionPreference = 'Stop'
$lab = Join-Path $env:LOCALAPPDATA 'PleosSyncLab'
if (-not $env:JAVA_HOME) { $env:JAVA_HOME = Join-Path $lab 'jdk' }
if (-not $env:ANDROID_HOME) { $env:ANDROID_HOME = Join-Path $lab 'sdk' }
$project = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../android'))
Push-Location $project
try {
    if ($Release) {
        if (-not $env:PLEOS_KEYSTORE -or -not $env:PLEOS_STORE_PASSWORD -or -not $env:PLEOS_KEY_PASSWORD) {
            throw 'Set PLEOS_KEYSTORE, PLEOS_STORE_PASSWORD and PLEOS_KEY_PASSWORD to your private signing key. Alias: submission.'
        }
        & .\gradlew.bat :app:testDebugUnitTest :app:assembleRelease --console=plain --max-workers=2
    } else { & .\gradlew.bat :app:assembleDebug :app:testDebugUnitTest --console=plain --max-workers=2 }
    if ($LASTEXITCODE -ne 0) { throw "Gradle failed: $LASTEXITCODE" }
} finally { Pop-Location }
