"""
Simple API test using PowerShell.
Run this with: .\test_api_request.ps1
"""

# Test welcome template
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Testing Welcome Template Email" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$body = @{
    recipients = @('exateks@gmail.com')
    template_name = 'welcome'
    context = @{
        user_name = 'Muhammad Salah'
        verify_url = 'https://example.com/verify/abc123xyz'
    }
} | ConvertTo-Json -Depth 5

try {
    $response = Invoke-RestMethod -Uri 'http://localhost:8000/api/email/send-template' `
        -Method POST `
        -Body $body `
        -ContentType 'application/json' `
        -ErrorAction Stop
    
    Write-Host "✅ Success: $($response.success)" -ForegroundColor Green
    Write-Host "Message: $($response.message)" -ForegroundColor Green
    Write-Host "Total Sent: $($response.total_sent)" -ForegroundColor Green
    Write-Host "Total Failed: $($response.total_failed)" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

Write-Host "`nCheck your email inbox at exateks@gmail.com`n"
