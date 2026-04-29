"""
Custom Checkov policy to validate required tags on AWS resources in Terraform plan.
This policy works with terraform_plan framework to see tags_all and module-created
resources.
"""

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

from config import VALID_TAG_VALUES, REQUIRED_TAGS
from helpers import unwrap, is_empty


class RequiredTagsCheck(BaseResourceCheck):
    def __init__(self):
        super().__init__(
            name="Ensure resource has all required tags with valid values",
            id="CKV_AWS_TAG_001",
            categories=[CheckCategories.GENERAL_SECURITY],
            supported_resources=["*"],
        )
        self.details = ""

    def scan_resource_conf(self, conf):
        if not isinstance(conf, dict):
            return CheckResult.UNKNOWN

        tags = unwrap(conf.get("tags"))
        tags_all = unwrap(conf.get("tags_all"))

        if tags is None and tags_all is None:
            return CheckResult.UNKNOWN

        effective_tags = tags_all if tags_all else tags

        if not isinstance(effective_tags, dict):
            effective_tags = {}

        processed_tags = self.parse_tags(effective_tags)

        missing = processed_tags.get("missing", [])
        invalid = processed_tags.get("invalid", [])

        problems = []

        if missing:
            problems.append(f"Missing tags: {', '.join(missing)}")

        if invalid:
            problems.append(f"Invalid values: {'; '.join(invalid)}")

        if problems:
            self.details = " | ".join(problems)
            return CheckResult.FAILED

        return CheckResult.PASSED

    def parse_tags(self, effective_tags):
        missing = []
        invalid = []

        for tag in REQUIRED_TAGS:
            if tag not in effective_tags:
                missing.append(tag)
                continue

            tag_value = unwrap(effective_tags[tag])

            if is_empty(tag_value):
                missing.append(f"{tag} (empty)")
                continue

            if isinstance(tag_value, bool):
                tag_value = str(tag_value).lower()

            valid_tag_values = VALID_TAG_VALUES.get(tag, False)

            if valid_tag_values:

                print(f"valid values: {valid_tag_values}")
                print(f"value: {tag_value}")

                if tag_value not in valid_tag_values:
                    invalid.append(
                        f"{tag}='{tag_value}' (valid: {', '.join(valid_tag_values)})"
                    )

        return {"missing": missing, "invalid": invalid}


check = RequiredTagsCheck()
