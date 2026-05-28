#!/usr/bin/env python3
"""
Parses Checkov JSON output and generates GitHub Action outputs.
"""

import json
import os
import sys


def parse_violations(json_file):
    """Read a Checkov JSON file and return a list of tag-violation dicts."""
    violations = []
    try:
        with open(json_file, encoding="utf-8") as f:
            results = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Warning: Could not parse {json_file}: {e}")
        return violations

    return extract_checkov_results(results)

def extract_checkov_results(results_dict):
    violations = []
    for check in results_dict.get("results", {}).get("failed_checks", []):
        violations.append(
            {
                "resource": check.get("resource", ""),
                "message": check.get("check_name", ""),
                "details": check.get("details"),
            }
        )

    return violations

def build_summary(violations):
    """Build a markdown summary string from a list of violations."""
    if not violations:
        return "✅ **All resources have required tags**"

    lines = [f"❌ **Found {len(violations)} tag violation(s)**\n"]
    for v in violations:
        resource = v["resource"]
        if resource.startswith("module."):
            module_name = resource.split(".")[1]
            hint = f"Check `modules/{module_name}/`"
        else:
            resource_name = (
                resource.split(".")[1] if "." in resource else resource
            )
            hint = f'Look for `resource ... "{resource_name}"`'

        lines.append(f"- **{resource}**")
        lines.append(f"  - 💡 {hint}")
        lines.append(f"  - Details: {v['details']}")
        lines.append(f"  - ❌ {v['message']}")

    return "\n".join(lines)


def main():
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    results_file_path = "./results_json.json"

    violations = parse_violations(results_file_path)

    violations_count = len(violations)
    passed = violations_count == 0
    summary = build_summary(violations)

    print(f"\n📊 Violations: {violations_count}")
    print(summary)

    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"violations_count={violations_count}\n")
            f.write(f"passed={str(passed).lower()}\n")
            f.write(f"violations_summary<<EOF\n{summary}\nEOF\n")

    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
