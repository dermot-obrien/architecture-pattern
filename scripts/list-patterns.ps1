# List all patterns in the workspace
# Usage: .\scripts\list-patterns.ps1 [-Path <directory>]

param(
    [string]$Path = "."
)

Write-Host "Searching for patterns in: $Path" -ForegroundColor Cyan
Write-Host ""

# Find all index.md files that have pattern metadata
Get-ChildItem -Path $Path -Recurse -Filter "index.md" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    
    # Check if file has pattern front matter
    if ($content -match "(?m)^title:" -and $content -match "(?m)^id:") {
        $dir = $_.DirectoryName
        
        # Extract pattern info
        $title = ""
        $id = ""
        $version = ""
        
        if ($content -match "(?m)^title:\s*(.+)$") {
            $title = $matches[1].Trim('"')
        }
        if ($content -match "(?m)^id:\s*(.+)$") {
            $id = $matches[1].Trim('"')
        }
        if ($content -match "(?m)^version:\s*(.+)$") {
            $version = $matches[1].Trim('"')
        }
        
        if ($id) {
            Write-Host "[$id] $title" -ForegroundColor Green
            if ($version) {
                Write-Host "  Version: $version" -ForegroundColor Gray
            }
            Write-Host "  Path: $dir" -ForegroundColor Gray
            Write-Host ""
        }
    }
}

# Also look for patterns via model.py scan if available
$modelPath = ".agents\skills\model\bin\model.py"
if (Test-Path $modelPath) {
    Write-Host "---" -ForegroundColor Yellow
    Write-Host "Using model.py scan for validation:" -ForegroundColor Cyan
    Write-Host ""
    python $modelPath scan $Path --recursive 2>&1 | Select-String -Pattern "^(PAT-|REF-|UC-)" | ForEach-Object {
        Write-Host $_.Line
    }
}
