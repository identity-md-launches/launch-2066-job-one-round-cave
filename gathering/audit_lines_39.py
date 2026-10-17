#!/usr/bin/env python3
"""Run reviewed line checks/demos; keep compact evidence and line files intact."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('previous_audit', ROOT/'gathering/audit_lines_38.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)


def run_line(line):
    rows = []
    for name, kind, command, expected in previous.jobs(line):
        if name == 'planseal' and kind == 'demo':
            command[-1] = 'demo'
        if name in ('tuplecheck', 'apidelta') and kind == 'check':
            command = ['python3', '-B', 'gathering/scratch_suite_39.py',
                       f'line-4/tools/{name}/selftest.py']
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=120)
        combined = result.stdout + result.stderr
        tests = re.search(r'Ran (\d+) tests?', combined)
        passed = result.returncode == expected
        rows.append(dict(line=line, tool=name, kind=kind, command=command,
            expected_exit=expected, actual_exit=result.returncode, passed=passed,
            unittest_cases=int(tests[1]) if tests else 0,
            output_sha256=hashlib.sha256(combined.encode()).hexdigest(),
            evidence=combined[-160:] if passed else combined[-1800:]))
    return rows


def main():
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = [row for group in pool.map(run_line, range(1,5)) for row in group]
    summary = [dict(line=n, tools=len({r['tool'] for r in rows if r['line']==n}),
        commands=sum(r['line']==n for r in rows),
        unittest_cases=sum(r['unittest_cases'] for r in rows if r['line']==n),
        unexpected=sum(not r['passed'] for r in rows if r['line']==n)) for n in range(1,5)]
    raw = json.dumps(dict(round=39, summary=summary, commands=rows), separators=(',',':'))+'\n'
    assert len(raw.encode()) < 100000
    (ROOT/'gathering/audit-lines-39.json').write_text(raw)
    print(json.dumps(summary, indent=2))
    for row in rows:
        if not row['passed']: print(json.dumps(row, indent=2))
    return int(any(not r['passed'] for r in rows))


if __name__ == '__main__':
    raise SystemExit(main())
