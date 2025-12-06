# Performance test automation (JMeter)

This repository contains a scaffold to automate JMeter performance testing in GitHub Actions.

Quick start (local, Docker required):

1. Patch the baseline JMX (or edit manually):

```powershell
python scripts/patch_jmx.py --input tests/jmeter/baseline.jmx --output tests/jmeter/modified.jmx --users 5 --csv tests/jmeter/data/params.csv
```

2. Run JMeter via Docker:

```powershell
ci\run_jmeter.ps1
```

Or on Unix/macOS:

```bash
./ci/run_jmeter.sh
```

3. Parse results and check thresholds:

```powershell
python scripts/parse_results.py --input artifacts/results.jtl --output artifacts/metrics.json --p95 2000 --error_rate 1.0
```

CI: `.github/workflows/perf-test.yml` runs a smoke test on PRs and full tests on schedule. Artifacts are uploaded to the workflow run.

Next steps:
- Customize `tests/jmeter/baseline.jmx` with your recorded scenario.
- Update `reports/template` to change the HTML report layout.
- Consider using a self-hosted runner for high-load tests.
