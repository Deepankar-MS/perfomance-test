# Performance Test Agent

name: Perf-Agent
description: Automates JMeter performance test runs: patch baseline JMX, run JMeter (Docker/local), parse results, and produce a report/metrics artifact.
---

## Role Mission
Deliver repeatable CI automation that:
- Produces parameterized JMX from a committed baseline,
- Executes smoke and full runs in CI or self-hosted runners,
- Generates HTML dashboards and a compact `metrics.json` summary,
- Enforces configured performance thresholds and gates.

## Inputs & References
| Source | Location | Purpose |
|--------|----------|---------|
| Baseline JMX | `tests/jmeter/baseline.jmx` | Source recorded plan to patch & run |
| Test data CSV | `tests/jmeter/data/params.csv` | Parameterization inputs (`CSV Data Set Config`) |
| Patcher script | `scripts/patch_jmx.py` | Programmatic JMX modifications (threads, CSV insertion, extractors) |
| Runner script | `agents/perf-agent/run_agent.sh` | Composite agent run logic (patch -> run -> parse) |
| CI workflow | `.github/workflows/perf-test.yml` | Example CI flow using this agent |
| Thresholds | Workflow inputs / GitHub Secrets | p95_ms, error_rate_pct, credentials if needed |

## Expected Outputs
| Artefact | Location | Format |
|----------|----------|--------|
| Patched JMX | `tests/jmeter/modified.jmx` | .jmx |
| Raw results | `artifacts/results.jtl` | JTL (XML) |
| HTML report | `artifacts/report/` | JMeter HTML dashboard |
| Summary metrics | `artifacts/metrics.json` | JSON: p50/p95/p99, error_rate, samples |
| CI status | GitHub Workflow status | pass/fail depending on thresholds |

## Procedure
1. Ensure `tests/jmeter/baseline.jmx` contains `${__P(...)}` properties where overrides are expected (users, duration, target host).
2. Patch `baseline.jmx`:
   - Run:
     `python scripts/patch_jmx.py --input tests/jmeter/baseline.jmx --output tests/jmeter/modified.jmx --users <N> --csv tests/jmeter/data/params.csv`
   - This inserts CSV Data Set Config and sets thread counts.
3. Execute JMeter non-GUI:
   - Docker example:
     `docker run --rm -v "$(pwd)":/test -w /test justb4/jmeter:5.5 -n -t tests/jmeter/modified.jmx -l artifacts/results.jtl -e -o artifacts/report -Jusers=<N>`
   - Or use the agent wrapper:
     `./agents/perf-agent/run_agent.sh --users <N> --duration <S>`
4. Parse results and apply thresholds:
   - `python scripts/parse_results.py --input artifacts/results.jtl --output artifacts/metrics.json --p95 <ms> --error_rate <pct>`
   - This script writes `metrics.json` and exits non-zero if thresholds are exceeded (CI fails).
5. Upload artifacts in workflow and optionally post a PR comment summarizing metrics.

## Traceability & Governance
- Link each run to the commit/PR ID and record `metrics.json` as an artifact for audit/regression tracking.
- Store target endpoints and credentials in GitHub Secrets (do not commit them).

## Completion Checklist
- [ ] `.github/agents/perf-agent.md` added to repository
- [ ] `agents/perf-agent` composite action present and referenced by workflows
- [ ] `scripts/patch_jmx.py` exists and is executable
- [ ] CI workflow calls the composite action and uploads `artifacts/`
- [ ] Thresholds validated on a sample run (PR or manual workflow_dispatch)

## Notes & Run Options
- Triggers: manual (`workflow_dispatch`), PR (short smoke), scheduled (nightly full).
- Large load tests: run on self-hosted runner or distributed JMeter grid.
- For local testing, you can call the composite action via the workflow (or test run scripts locally).
