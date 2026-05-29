# COAT Tag Validator

[![Ministry of Justice Repository Compliance Badge](https://github-community.service.justice.gov.uk/repository-standards/api/coat-tag-validator/badge)](https://github-community.service.justice.gov.uk/repository-standards/coat-tag-validator)

This action:

- Prevents untagged resources from being deployed by failing PRs with missing and invalid tags
- Enforces consistency across teams by validating against a defined tag policy
- Reduces remediation costs by catching issues at PR time, not after deployment
- Supports FinOps and compliance by ensuring resources are properly attributed

## How to use

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
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@ec61189d14ec14c8efccab744f656cffd0e33f37  # v6.1.0
        with:
          role-to-assume: "arn:aws:iam::111111111111:role/my-read-only-role"
          role-session-name: "myrolesessionname"
          aws-region: "eu-west-2"

      - name: Validate Tags
        id: validate
        uses: ministryofjustice/coat-tag-validator@e0cccd30f5f5f01aa0902d42d79e5c7b32b78cbf #v2.1.0
        with:
          terraform_directory: ./terraform
```

## Inputs

| Input | Description | Required | Default |
| ------- | ------------- | ---------- | --------- |
| `terraform_directory` | Path to Terraform files | Yes | `.` |
| `terraform_workspace` | Terraform workspace | No | `` |
| `terraform_plan_backend` | `local` plans all resources via a temporary local backend override (default). `remote` uses your configured backend and state (requires credentials). | No | `local` |