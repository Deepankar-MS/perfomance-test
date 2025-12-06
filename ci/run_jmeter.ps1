Param(
  [string]$JMX = "tests/jmeter/modified.jmx",
  [int]$USERS = 1,
  [int]$DURATION = 60,
  [string]$REPORT_DIR = "artifacts/report",
  [string]$RESULTS = "artifacts/results.jtl"
)

New-Item -ItemType Directory -Path artifacts -Force | Out-Null
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $REPORT_DIR
New-Item -ItemType Directory -Path $REPORT_DIR -Force | Out-Null

if (Get-Command docker -ErrorAction SilentlyContinue) {
  Write-Host "Running JMeter in Docker (justb4/jmeter:5.5)"
  docker run --rm -v ${PWD}:/test -w /test justb4/jmeter:5.5 `
    -n -t $JMX -l $RESULTS -j artifacts/jmeter.log -Jusers=$USERS -Jduration=$DURATION -e -o $REPORT_DIR
} else {
  Write-Host "Docker not found; attempting to run local jmeter binary"
  jmeter -n -t $JMX -l $RESULTS -j artifacts/jmeter.log -Jusers=$USERS -Jduration=$DURATION -e -o $REPORT_DIR
}

Write-Host "JMeter run complete. Results: $RESULTS Report dir: $REPORT_DIR"
