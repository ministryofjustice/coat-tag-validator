#!/usr/bin/env python3
"""
Parses Checkov JSON output and generates GitHub Action outputs.
"""

import glob
import json
import os
import sys


def _format_details(value):
    """Normalise Checkov's `details` field (list or str) to a single string."""
    if isinstance(value, list):
        return " | ".join(str(v).strip() for v in value if v)
    if isinstance(value, str):
        return value.strip()
    return ""


def parse_violations(json_file):
    """Read a Checkov JSON file and return a list of tag-violation dicts."""
    violations = []
    try:
        with open(json_file, encoding="utf-8") as f:
            results = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Warning: Could not parse {json_file}: {e}")
        return violations

    for check in results.get("results", {}).get("failed_checks", []):
        if "CKV_AWS_TAG" not in check.get("check_id", ""):
            continue

        file_line_range = check.get("file_line_range", [0, 0])
        start_line = file_line_range[0] if file_line_range else 0
        end_line = (
            file_line_range[1] if len(file_line_range) > 1 else start_line
        )

        violations.append(
            {
                "resource": check.get("resource", "Unknown"),
                "file": check.get("file_path", "Unknown"),
                "start_line": start_line,
                "end_line": end_line,
                "check": check.get("check_id", "Unknown"),
                "message": check.get("check_name", "Missing required tags"),
                "details": _format_details(check.get("details")),
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
    terraform_dir = os.environ.get("TERRAFORM_DIR", ".")
    soft_fail = os.environ.get("SOFT_FAIL", "false").lower() == "true"
    github_output = os.environ.get("GITHUB_OUTPUT", "")

    json_files = glob.glob(os.path.join(terraform_dir, "results_*.json"))

    violations = []
    for json_file in json_files:
        violations.extend(parse_violations(json_file))

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

    if not passed and not soft_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
