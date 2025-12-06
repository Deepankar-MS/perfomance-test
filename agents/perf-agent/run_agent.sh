#!/usr/bin/env bash
set -euo pipefail

USERS=5
DURATION=60
JMX="tests/jmeter/baseline.jmx"
CSV="tests/jmeter/data/params.csv"
P95=2000
ERROR_RATE=1.0

usage() {
  cat <<EOF
Usage: run_agent.sh [--users N] [--duration S] [--jmx path] [--csv path] [--p95 ms] [--error_rate pct]
EOF
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --users) USERS="$2"; shift 2;;
    --duration) DURATION="$2"; shift 2;;
    --jmx) JMX="$2"; shift 2;;
    --csv) CSV="$2"; shift 2;;
    --p95) P95="$2"; shift 2;;
    --error_rate) ERROR_RATE="$2"; shift 2;;
    --help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

echo "Perf agent starting: users=$USERS duration=$DURATION jmx=$JMX csv=$CSV p95=$P95 error_rate=$ERROR_RATE"

MODIFIED_JMX="tests/jmeter/modified.jmx"

cleanup() {
  rc=$?
  echo "Perf agent exiting with code $rc"
  exit $rc
}
trap cleanup EXIT

if [[ ! -f "$JMX" ]]; then
  echo "Input JMX not found: $JMX" >&2
  exit 2
fi

if [[ -n "$CSV" && ! -f "$CSV" ]]; then
  echo "CSV not found: $CSV" >&2
  exit 2
fi

python scripts/patch_jmx.py --input "$JMX" --output "$MODIFIED_JMX" --users "$USERS" --csv "$CSV"

export USERS DURATION
REPORT_DIR=artifacts/report
RESULTS=artifacts/results.jtl

mkdir -p artifacts "$REPORT_DIR"

if command -v docker >/dev/null 2>&1; then
  echo "Running JMeter via Docker"
  docker pull justb4/jmeter:5.5 >/dev/null 2>&1 || true
  docker run --rm -v "$(pwd)":/test -w /test justb4/jmeter:5.5 \
    -n -t "$MODIFIED_JMX" -l "$RESULTS" -j artifacts/jmeter.log -Jusers="$USERS" -Jduration="$DURATION" -e -o "$REPORT_DIR"
else
  echo "Docker not found; attempting local jmeter"
  if ! command -v jmeter >/dev/null 2>&1; then
    echo "jmeter binary not found; install JMeter or install Docker." >&2
    exit 3
  fi
  jmeter -n -t "$MODIFIED_JMX" -l "$RESULTS" -j artifacts/jmeter.log -Jusers="$USERS" -Jduration="$DURATION" -e -o "$REPORT_DIR"
fi

python scripts/parse_results.py --input "$RESULTS" --output artifacts/metrics.json --p95 "$P95" --error_rate "$ERROR_RATE"

echo "Perf agent finished. Artifacts in artifacts/"
