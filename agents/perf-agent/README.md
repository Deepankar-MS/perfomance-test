# perf-agent

This is a reusable GitHub "agent" (composite action) that automates a JMeter performance test run:
- patches a baseline JMX (`scripts/patch_jmx.py`)
- runs JMeter (Docker or local)
- parses results and produces `artifacts/metrics.json`

Usage in a workflow (example):

```yaml
jobs:
  perf:
    uses: ./agents/perf-agent
    with:
      users: '10'
      duration: '120'
      jmx_path: 'tests/jmeter/baseline.jmx'
      csv_path: 'tests/jmeter/data/params.csv'
      p95: '2000'
      error_rate: '1.0'
```

Outputs: artifacts (uploaded by the calling workflow) include `artifacts/results.jtl`, `artifacts/report/`, `artifacts/jmeter.log`, and `artifacts/metrics.json`.

Notes:
- This composite action expects the repository to contain the scripts in `scripts/` and `ci/` from the repo scaffold.
- For heavy load tests run this on a self-hosted runner with adequate CPU/memory and network capacity.

Action outputs
- `metrics-json-path`: path to `artifacts/metrics.json` (if produced)
- `report-path`: path to `artifacts/report` (if produced)

Runner recommendations
- For smoke tests: GitHub-hosted `ubuntu-latest` is fine.
- For full-scale production load tests: use self-hosted Linux runners with >=8 CPU cores and >=16GB RAM, or run a distributed JMeter grid.
