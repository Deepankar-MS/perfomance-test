Param(
  [int]$Users = 5,
  [int]$Duration = 60,
  [string]$Jmx = "tests/jmeter/baseline.jmx",
  [string]$Csv = "tests/jmeter/data/params.csv",
  [int]$P95 = 2000,
  [double]$ErrorRate = 1.0
)

$ErrorActionPreference = 'Stop'

Write-Host "Perf agent starting: users=$Users duration=$Duration jmx=$Jmx csv=$Csv p95=$P95 error_rate=$ErrorRate"

Try {
    $ModifiedJmx = "tests/jmeter/modified.jmx"

    if (-Not (Test-Path -Path $Jmx)) { throw "Input JMX not found: $Jmx" }
    if ($Csv -and -Not (Test-Path -Path $Csv)) { throw "CSV not found: $Csv" }

    python scripts/patch_jmx.py --input $Jmx --output $ModifiedJmx --users $Users --csv $Csv

    New-Item -ItemType Directory -Path artifacts -Force | Out-Null
    $ReportDir = "artifacts/report"
    $Results = "artifacts/results.jtl"
    if (Test-Path -Path $ReportDir) { Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $ReportDir }
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null

    if (Get-Command docker -ErrorAction SilentlyContinue) {
      Write-Host "Running JMeter via Docker"
      docker pull justb4/jmeter:5.5 | Out-Null
      docker run --rm -v ${PWD}:/test -w /test justb4/jmeter:5.5 `
        -n -t $ModifiedJmx -l $Results -j artifacts/jmeter.log -Jusers=$Users -Jduration=$Duration -e -o $ReportDir
    } else {
      Write-Host "Docker not found; attempting local jmeter"
      if (-Not (Get-Command jmeter -ErrorAction SilentlyContinue)) { throw "jmeter not found; install JMeter or Docker" }
      jmeter -n -t $ModifiedJmx -l $Results -j artifacts/jmeter.log -Jusers=$Users -Jduration=$Duration -e -o $ReportDir
    }

    python scripts/parse_results.py --input $Results --output artifacts/metrics.json --p95 $P95 --error_rate $ErrorRate

    Write-Host "Perf agent finished. Artifacts in artifacts/"
} Catch {
    Write-Error "Perf agent failed: $_"
    Exit 1
}
