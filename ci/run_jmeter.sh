#!/usr/bin/env bash
set -euo pipefail

# Simple wrapper to run JMeter inside Docker (uses justb4/jmeter)
USERS=${USERS:-1}
DURATION=${DURATION:-60}
REPORT_DIR=${REPORT_DIR:-artifacts/report}
RESULTS=${RESULTS:-artifacts/results.jtl}
JMX=${JMX:-tests/jmeter/modified.jmx}

mkdir -p artifacts
rm -rf "$REPORT_DIR" || true
mkdir -p "$REPORT_DIR"

if command -v docker >/dev/null 2>&1; then
  echo "Running JMeter in Docker (image: justb4/jmeter:5.5)"
  docker run --rm -v "$(pwd)":/test -w /test justb4/jmeter:5.5 \
    -n -t "$JMX" -l "$RESULTS" -j artifacts/jmeter.log -Jusers="$USERS" -Jduration="$DURATION" -e -o "$REPORT_DIR"
else
  echo "Docker not found; attempting to run local jmeter binary"
  jmeter -n -t "$JMX" -l "$RESULTS" -j artifacts/jmeter.log -Jusers="$USERS" -Jduration="$DURATION" -e -o "$REPORT_DIR"
fi

echo "JMeter run complete. Results: $RESULTS Report dir: $REPORT_DIR"
