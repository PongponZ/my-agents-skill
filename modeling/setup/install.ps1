# Windows wrapper: .\install.ps1            (interactive menu)
#                  .\install.ps1 all        (Claude Code + Codex + zip packages)
#                  .\install.ps1 claude-code --project C:\path\to\project
$py = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $py) { $py = (Get-Command py -ErrorAction SilentlyContinue) }
if (-not $py) { Write-Error "Python 3.10+ is required (https://www.python.org/downloads/)"; exit 1 }
& $py.Source "$PSScriptRoot\install_skills.py" @args
exit $LASTEXITCODE
