import json
import os
import sys


def parse_violations(json_file):
    violations = []
    try:
        with open(json_file, encoding="utf-8") as f:
            results = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Warning: Could not parse {json_file}: {e}")
        return violations

    return extract_checkov_results_to_mrkdwn(results)

def extract_checkov_results_to_mrkdwn(results_dict):
    unpacked_checks = results_dict.get("results", {}).get("failed_checks", [])

    if not unpacked_checks:
        return "✅ **All resources have required tags**"

    summary_lines = [f"❌ **Found {len(unpacked_checks)} tag violation(s)**\n"]
    for check in unpacked_checks:
        summary_lines.append(f"- Resource: {check.get("resource", "")}")
        summary_lines.append(f"  - ❌ {check.get("check_name", "")}")
        summary_lines.append(f"  - Details: {check.get('details', "")}")

    return "\n".join(summary_lines)


def main():
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    results_file_path = "./results_json.json"

    violations = parse_violations(results_file_path)

    violations_count = len(violations)
    passed = violations_count == 0
    summary = build_mrkdwn_summary(violations) if violations else "✅ **All resources have required tags**"

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
