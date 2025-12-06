# perf-agent Folder Structure

Layout and purpose of files under `agents/perf-agent`:

- `action.yml` - Composite action metadata. Import this action from workflows with `uses: ./agents/perf-agent`.
- `run_agent.sh` - Bash wrapper used by the action to run patch -> jmeter -> parse flow.
- `run_agent.ps1` - PowerShell wrapper for Windows/self-hosted runners.
- `README.md` - Usage instructions and example workflow snippet.
- `DEPENDENCIES.md` - Required software and install steps.

The action assumes these repository-level files exist (provided in repo scaffold):
- `tests/jmeter/baseline.jmx`
- `tests/jmeter/data/params.csv`
- `scripts/patch_jmx.py`
- `scripts/parse_results.py`
- `ci/run_jmeter.sh` (helper)
