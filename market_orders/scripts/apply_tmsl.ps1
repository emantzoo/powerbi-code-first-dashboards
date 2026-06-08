$ErrorActionPreference = "Stop"
$amo = "C:\tmp\tom\amo\lib\net45"
Add-Type -Path "$amo\Microsoft.AnalysisServices.Core.dll"
Add-Type -Path "$amo\Microsoft.AnalysisServices.Tabular.dll"

$port = "localhost:60507"
$srv = New-Object Microsoft.AnalysisServices.Tabular.Server
$srv.Connect($port)
$dbid = $srv.Databases[0].ID
Write-Host "Target DB: $dbid"

function Exec-Tmsl($file) {
    $json = (Get-Content -Raw -Path $file -Encoding UTF8).Replace("%DBNAME%", $dbid)
    $res = $srv.Execute($json)
    $errs = @()
    foreach ($r in $res) {
        foreach ($m in $r.Messages) {
            if ($m -is [Microsoft.AnalysisServices.XmlaError]) { $errs += $m.Description }
        }
    }
    if ($errs.Count -gt 0) { throw ("TMSL errors in $file :`n" + ($errs -join "`n")) }
    Write-Host "Applied: $file"
}

Exec-Tmsl "C:\tmp\table_orderevents.tmsl.json"
Exec-Tmsl "C:\tmp\table_measures.tmsl.json"

# Refresh data + recalc so the M partition loads and calculated columns/measures evaluate.
$srv.Refresh()
$db = $srv.Databases[$dbid]
$db.Model.RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)
$db.Model.SaveChanges() | Out-Null
Write-Host "Refresh complete."

$srv.Disconnect()
Write-Host "DONE_OK"
