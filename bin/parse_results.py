import json
import os


def parse_violations(json_file):
    violations = {}
    try:
        with open(json_file, encoding="utf-8") as f:
            results = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Warning: Could not parse {json_file}: {e}")
        return violations

    return extract_checkov_results(results)


def extract_checkov_results(results_dict):
    unpacked_checks = results_dict.get("results", {}).get("failed_checks", [])

    if not unpacked_checks:
        return {
            "summary": "✅ **All resources have required tags**",
            "violation_count": 0,
        }

    summary_lines = [f"❌ **Found {len(unpacked_checks)} tag violation(s)**\n"]
    for check in unpacked_checks:
        summary_lines.append(f"- Resource: {check.get("resource", "")}")
        summary_lines.append(f"  - ❌ {check.get("check_name", "")}")
        summary_lines.append(f"  - Details: {check.get('details', "")}")

    return {
        "summary": "\n".join(summary_lines),
        "violation_count": len(unpacked_checks),
    }


def main():
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    results_file_path = "./results_json.json"

    violations = parse_violations(results_file_path)

    print(violations.get("summary", ""))

    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"violations_summary<<EOF\n{violations.get("summary", "")}\nEOF\n")


if __name__ == "__main__":
    main()
