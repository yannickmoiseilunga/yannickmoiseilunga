# Windows-native publisher: does NOT call Bash or WSL.
# Publishes the extracted source bundle to the authenticated user's public GitHub profile repo.
# Installs Git via winget only with explicit permission; no tokens are requested or logged.
param()
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$RepoUrl = 'https://github.com/yannickmoiseilunga/yannickmoiseilunga.git'
$PublicUrl = 'https://github.com/yannickmoiseilunga/yannickmoiseilunga/tree/main/research/principia-ai-laboratory'
$Target = 'research/principia-ai-laboratory'
$Source = $PSScriptRoot
$LogPath = Join-Path $Source 'principia_publish_log.txt'
$script:GitExecutable = $null
$script:TemporaryRoot = $null

function Note([string] $Message) {
    $stamp = (Get-Date).ToString('HH:mm:ss')
    Write-Host "[$stamp] $Message"
    try { Add-Content -LiteralPath $LogPath -Value "[$stamp] $Message" -Encoding UTF8 } catch {}
}

function Find-Git {
    $resolved = Get-Command git.exe -ErrorAction SilentlyContinue
    if ($resolved) { return $resolved.Source }
    $candidates = @(
        (Join-Path $env:LOCALAPPDATA 'Programs\Git\cmd\git.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Git\bin\git.exe'),
        (Join-Path $env:ProgramFiles 'Git\cmd\git.exe'),
        (Join-Path $env:ProgramFiles 'Git\bin\git.exe'),
        (Join-Path ${env:ProgramFiles(x86)} 'Git\cmd\git.exe')
    )
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate -PathType Leaf)) {return $candidate}
    }
    # GitHub Desktop includes a copy of Git, even if it is absent from PATH.
    $desktop = Join-Path $env:LOCALAPPDATA 'GitHubDesktop'
    if (Test-Path $desktop) {
        $possible = Get-ChildItem -LiteralPath $desktop -Filter 'app-*' -Directory -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending |
            ForEach-Object { Join-Path $_.FullName 'resources\app\git\cmd\git.exe' }
        foreach ($candidate in $possible) {
            if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
        }
    }
    return $null
}

function Run-Git([string[]] $Arguments, [string] $Operation) {
    & $script:GitExecutable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Git failed during '$Operation' (exit code $LASTEXITCODE)."
    }
}

try {
    Note 'Starting Windows-native publication; no WSL, Bash or VS Code shell needed.'
    if (-not (Test-Path -LiteralPath (Join-Path $Source 'versions\v1\main.py'))) { throw 'Version 1 source not found. Extract the full ZIP before running.' }
    if (-not (Test-Path -LiteralPath (Join-Path $Source 'versions\v2\main.py'))) { throw 'Version 2 source not found. Extract the full ZIP before running.' }
    if (-not (Test-Path -LiteralPath (Join-Path $Source 'versions\v3\main.py'))) { throw 'Version 3 source not found. Extract the full ZIP before running.' }

    $script:GitExecutable = Find-Git
    if (-not $script:GitExecutable) {
        Note 'Git for Windows was not detected.'
        $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
        if (-not $winget) { throw 'Git and winget were not found. Install Git for Windows from https://git-scm.com/downloads/win and rerun this .bat file.' }
        Write-Host ''
        $reply = Read-Host 'Install Git for Windows automatically using winget? [Y/N]'
        if ($reply -notmatch '^(?i:y|yes)$') { throw 'Installation declined. Install Git for Windows from https://git-scm.com/downloads/win and rerun.' }
        Note 'Installing Git for Windows for the current user. This may take several minutes.'
        & $winget.Source install --id Git.Git -e --source winget --scope user --accept-package-agreements --accept-source-agreements --disable-interactivity
        if ($LASTEXITCODE -ne 0) {
            throw "winget returned exit code $LASTEXITCODE. Install Git manually from https://git-scm.com/downloads/win and rerun."
        }
        $script:GitExecutable = Find-Git
        if (-not $script:GitExecutable) { throw 'Git was installed but its executable could not be located in this session. Close this window, reopen Windows Terminal, then run the .bat again.' }
    }
    Note "Using Git: $script:GitExecutable"
    $gitVersion = & $script:GitExecutable --version
    Note "$gitVersion"

    $script:TemporaryRoot = Join-Path $env:TEMP ("principia-publish-" + [Guid]::NewGuid().ToString('N'))
    $repoDir = Join-Path $script:TemporaryRoot 'repo'
    New-Item -ItemType Directory -Path $script:TemporaryRoot -Force | Out-Null
    Note 'Cloning the public repository, branch main.'
    Run-Git @('clone','--depth','1','--single-branch','--branch','main',$RepoUrl,$repoDir) 'repository clone'

    $destination = Join-Path $repoDir 'research\principia-ai-laboratory'
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    Note 'Copying all three versions, source code, reports and documentation.'
    $robocopy = Join-Path $env:SystemRoot 'System32\robocopy.exe'
    & $robocopy $Source $destination /E /R:1 /W:1 /NP /NFL /NDL /NJH /NJS /XD .git __pycache__ .venv venv .pytest_cache /XF principia_publish_log.txt
    $copyStatus = $LASTEXITCODE
    if ($copyStatus -ge 8) { throw "File copy failed (robocopy exit code $copyStatus)." }

    $workflowSrc = Join-Path $Source '.github\workflows\checks.yml'
    if (Test-Path $workflowSrc) {
        $workflowDest = Join-Path $repoDir '.github\workflows'
        New-Item -ItemType Directory -Path $workflowDest -Force | Out-Null
        Copy-Item -LiteralPath $workflowSrc -Destination (Join-Path $workflowDest 'principia-lab-checks.yml') -Force
    }
    Run-Git @('-C',$repoDir,'add','--',$Target) 'stage research files'
    foreach ($v in @('v1','v2','v3')) {
        $reports = "$Target/versions/$v/reports"
        if (Test-Path (Join-Path $repoDir ($reports -replace '/', '\'))) {
            Run-Git @('-C',$repoDir,'add','-f','--',$reports) "stage frozen $v evidence"
        }
    }
    if (Test-Path $workflowSrc) {
        Run-Git @('-C',$repoDir,'add','--','.github/workflows/principia-lab-checks.yml') 'stage GitHub Actions'
    }

    & $script:GitExecutable -C $repoDir diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Note 'Everything is already published; there are no new changes.'
        Note "Published: $PublicUrl"
        exit 0
    }
    if ($LASTEXITCODE -ne 1) { throw 'Unable to inspect staged Git changes.' }

    # Set identity for this temporary clone only; do not modify the user's global Git settings.
    $name = & $script:GitExecutable -C $repoDir config --get user.name 2>$null
    if (-not $name) { Run-Git @('-C',$repoDir,'config','user.name','yannickmoiseilunga') 'set local commit author' }
    $email = & $script:GitExecutable -C $repoDir config --get user.email 2>$null
    if (-not $email) { Run-Git @('-C',$repoDir,'config','user.email','54799716+yannickmoiseilunga@users.noreply.github.com') 'set local commit email' }

    Write-Host ''
    Note 'Committing the three version folders and documented evidence.'
    Run-Git @('-C',$repoDir,'commit','-m','Publish complete Principia AI Laboratory versions 1, 2 and 3') 'commit'
    Note 'Pushing to GitHub. A Git Credential Manager browser sign-in may appear now.'
    Note 'Do not enter your GitHub password or token into this chat or publication files.'
    Run-Git @('-C',$repoDir,'push','origin','HEAD:main') 'push to public GitHub'
    $head = (& $script:GitExecutable -C $repoDir rev-parse HEAD).Trim()
    Note "Published commit: $head"
    Note "Published: $PublicUrl"
    exit 0
}
catch {
    Write-Host ''
    Note ("PUBLICATION FAILED: " + $_.Exception.Message)
    Write-Host 'If Git authentication fails: open Git Bash, run git credential-manager github login, then rerun the .bat.' -ForegroundColor Yellow
    Write-Host ('Log: ' + $LogPath) -ForegroundColor Yellow
    exit 1
}
finally {
    if ($script:TemporaryRoot -and (Test-Path -LiteralPath $script:TemporaryRoot)) {
        try {Remove-Item -LiteralPath $script:TemporaryRoot -Recurse -Force -ErrorAction Stop} catch {Note 'Temporary clone cleanup did not complete.'}
    }
}
