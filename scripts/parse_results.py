#!/usr/bin/env python3
"""
parse_results.py

Streaming JTL parser for large files. Produces metrics JSON and exits with codes:
  0 - OK
  2 - thresholds exceeded
  3 - parsing failure / input missing

Usage:
  python scripts/parse_results.py --input artifacts/results.jtl --output artifacts/metrics.json --p95 2000 --error_rate 1.0
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from typing import Dict


def parse_jtl_stream(path: str) -> Dict[str, int]:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    times = []
    errors = 0
    total = 0
    # Use iterparse to avoid building entire tree in memory
    for event, elem in ET.iterparse(path, events=("end",)):
        tag = elem.tag
        if tag.endswith('httpSample') or tag.endswith('sample'):
            total += 1
            t = elem.get('t')
            if t is None:
                time_elem = elem.find('time')
                t = time_elem.text if time_elem is not None else '0'
            try:
                times.append(int(t))
            except Exception:
                pass
            success = elem.get('s')
            if success is None:
                succ_elem = elem.find('success')
                success = succ_elem.text if succ_elem is not None else 'true'
            if str(success).lower() not in ('true', '1'):
                errors += 1
            # clear element to save memory
            elem.clear()
    times.sort()

    def pct(p: float) -> int:
        if not times:
            return 0
        k = max(0, int((p / 100.0) * len(times)) - 1)
        return times[k]

    return {
        'p50_ms': pct(50),
        'p95_ms': pct(95),
        'p99_ms': pct(99),
        'error_rate_pct': (errors / total * 100 if total > 0 else 0),
        'samples': total,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--p95', type=float, default=2000)
    parser.add_argument('--error_rate', type=float, default=1.0)
    args = parser.parse_args()

    try:
        metrics = parse_jtl_stream(args.input)
    except FileNotFoundError:
        print(f"Input JTL not found: {args.input}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"Failed parsing JTL: {e}", file=sys.stderr)
        sys.exit(3)

    # Add basic run metadata if available
    metadata = {
        'metrics': metrics,
        'run': {
            'commit': os.environ.get('GITHUB_SHA') or os.environ.get('CI_COMMIT_SHA') or None,
        },
    }

    try:
        with open(args.output, 'w', encoding='utf-8') as fh:
            json.dump(metadata, fh, indent=2)
    except Exception as e:
        print(f"Failed to write metrics JSON: {e}", file=sys.stderr)
        sys.exit(3)

    print(f"Wrote metrics to {args.output}")

    if metrics['p95_ms'] > args.p95 or metrics['error_rate_pct'] > args.error_rate:
        print('Thresholds exceeded:', metrics)
        sys.exit(2)
    print('Thresholds OK:', metrics)
    sys.exit(0)


if __name__ == '__main__':
    main()
