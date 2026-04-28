# Checkov Tag Validator

[![CI](https://github.com/ministryofjustice/checkov-tag-validator/actions/workflows/ci.yml/badge.svg)](https://github.com/ministryofjustice/checkov-tag-validator/actions/workflows/ci.yml)

> **Shift-left tag enforcement for Terraform PRs** — Catch missing or invalid tags before they reach production.

## Impact

Untagged AWS resources cost organisations money and create compliance gaps. This action:

- **Prevents untagged resources** from being deployed by failing PRs with missing and invalid tags
- **Enforces consistency** across teams by validating against a defined tag policy
- **Reduces remediation costs** by catching issues at PR time, not after deployment
- **Supports FinOps and compliance** by ensuring resources are properly attributed

## Features

- **Works with modules**: Validates tags on module-created resources via Terraform plan
- **Detects empty values**: Catches null, empty, or whitespace-only tag values
- **Supports default_tags**: Works with AWS provider `default_tags` via `tags_all`
- **Configurable**: Specify your own required tags or use MoJ defaults

## How It Differs From Standard Checkov

This action uses `terraform_plan` framework, not static file scanning. This means it can:

| Capability | Standard Checkov | This Action |
|------------|-----------------|-------------|
| See `tags_all` (merged default_tags + resource tags) | ❌ | ✅ |
| Validate module-created resources | ❌ | ✅ |
| Detect whitespace-only tag values | ❌ | ✅ |

**Note:** This action is designed to run alongside your existing Checkov workflows, not replace them. Standard Checkov handles security scanning; this action focuses specifically on tag enforcement.

## Quick Start

Create `.github/workflows/validate-tags.yml`:

```yaml
name: Validate Tags

on:
  pull_request:
    paths:
      - '**/*.tf'

permissions:
  contents: read
  pull-requests: write

jobs:
  validate-tags:
    name: Tag Validation
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Validate Tags
        id: validate
        uses: ministryofjustice/checkov-tag-validator@v1.0.2
        with:
          terraform_directory: ./terraform
          soft_fail: false

      - name: Post Results to PR
        if: always() && github.event_name == 'pull_request'
        uses: actions/github-script@v7
        env:
          SUMMARY: ${{ steps.validate.outputs.violations_summary }}
          PASSED: ${{ steps.validate.outputs.passed }}
        with:
          script: |
            const summary = process.env.SUMMARY || '✅ All resources have required tags';
            const passed = process.env.PASSED === 'true';
            const icon = passed ? '✅' : '⚠️';
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 🏷️ Tag Validation ${icon}\n\n${summary}`
            });
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `terraform_directory` | Path to Terraform files | Yes | `.` |
| `soft_fail` | Return exit code 0 even if violations found | No | `false` |

## Outputs

| Output | Description |
|--------|-------------|
| `violations_count` | Number of tag violations found |
| `violations_summary` | Markdown summary for PR comments |
| `passed` | Whether validation passed (`true`/`false`) |

## How It Works

1. **Generates Terraform plan**: Runs `terraform init` and `terraform plan` with dummy credentials
2. **Scans plan with Checkov**: Uses custom policy to check `tags_all` on all resources
3. **Reports violations**: Outputs violation count, pass/fail status, and markdown summary

## Integration Guide

### For Teams Adopting This Action

1. Add the workflow file to `.github/workflows/validate-tags.yml`
2. Ensure your Terraform can `init` without real credentials (use `backend = false`)
3. Optionally add PR comment integration for visibility

### Handling Violations

When violations are detected:
- The action exits with code 1 (fails the check)
- The `violations_summary` output contains markdown-formatted details
- Use `soft_fail: true` to report violations without failing the build