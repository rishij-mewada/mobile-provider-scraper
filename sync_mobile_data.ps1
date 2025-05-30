 
# Mobile Provider Pricing Data Sync Script
$ErrorActionPreference = "Continue"

# Configuration
$repoOwner = "rishij-mewada"
$repoName = "mobile-provider-scraper"
$localPath = "C:\Analytics\Dropbox\Mewada Analytics\Analytics Data\07. Product Development\Mobile Provider Pricing"
$logFile = "$localPath\sync_log.txt"

# Create directory if it doesn't exist
if (!(Test-Path $localPath)) {
    New-Item -ItemType Directory -Path $localPath -Force
}

# Log function
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp - $Message"
    Write-Host $logEntry
    Add-Content -Path $logFile -Value $logEntry
}

Write-Log "Starting mobile provider pricing data sync..."

try {
    # Get repository contents
    $apiUrl = "https://api.github.com/repos/$repoOwner/$repoName/contents"
    $response = Invoke-RestMethod -Uri $apiUrl -Method Get
    
    # Filter for CSV files
    $csvFiles = $response | Where-Object { $_.name -like "*.csv" }
    
    Write-Log "Found $($csvFiles.Count) CSV files in repository"
    
    foreach ($file in $csvFiles) {
        try {
            $fileName = $file.name
            $downloadUrl = $file.download_url
            $localFile = Join-Path $localPath $fileName
            
            # Download file
            Invoke-WebRequest -Uri $downloadUrl -OutFile $localFile
            Write-Log "Downloaded: $fileName"
            
        } catch {
            Write-Log "Error downloading $($file.name): $($_.Exception.Message)"
        }
    }
    
    Write-Log "Mobile provider pricing sync completed successfully"
    
} catch {
    Write-Log "Error during sync: $($_.Exception.Message)"
}
