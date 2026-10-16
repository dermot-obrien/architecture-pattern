# List all patterns in the workspace with validation
# Usage: .\scripts\list-patterns.ps1 [-Path <directory>] [-Verbose]

param(
    [string]$Path = ".",
    [switch]$Verbose
)

Write-Host "Searching for patterns in: $Path" -ForegroundColor Cyan
if ($Verbose) {
    Write-Host "(verbose mode enabled)" -ForegroundColor Gray
}
Write-Host ""

$modelPath = ".agents\skills\model\bin\model.py"
$modelAvailable = Test-Path $modelPath

# Find all index.md files that have pattern metadata
Get-ChildItem -Path $Path -Recurse -Filter "index.md" | Sort-Object FullName | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $file = $_.FullName
    
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
            # Try to validate if model.py is available
            $status = ""
            $validationOutput = ""
            if ($modelAvailable) {
                $validationOutput = python $modelPath validate $file 2>&1 | Out-String
                if ($validationOutput -match "0 problems") {
                    $status = " ✓"
                    $color = "Green"
                } else {
                    $status = " ✗"
                    $color = "Red"
                }
            } else {
                $color = "Yellow"
            }
            
            Write-Host "[$id]$status $title" -ForegroundColor $color
            if ($version) {
                Write-Host "  Version: $version" -ForegroundColor Gray
            }
            Write-Host "  Path: $dir" -ForegroundColor Gray
            
            # Show validation details in verbose mode
            if ($Verbose -and $modelAvailable) {
                Write-Host "  Validation:" -ForegroundColor Cyan
                $validationOutput -split "`n" | ForEach-Object {
                    if ($_.Trim()) {
                        Write-Host "    $_" -ForegroundColor Gray
                    }
                }
            }
            
            Write-Host ""
        }
    }
}

# Summary from model.py scan if available
if ($modelAvailable -and $Verbose) {
    Write-Host "---" -ForegroundColor Yellow
    Write-Host "Full scan results:" -ForegroundColor Cyan
    Write-Host ""
    python $modelPath scan $Path --recursive 2>&1
}
