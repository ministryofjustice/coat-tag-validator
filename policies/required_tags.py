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
        # Ensure configuration is a dictionary data type
        if not isinstance(conf, dict):
            return CheckResult.UNKNOWN

        tags = conf.get("tags", [])
        tags_all = conf.get("tags_all", [])

        # Account for untaggable resources - will not have a tags key
        if not tags:
            return CheckResult.PASSED
        # Account for completely empty tag set
        elif tags == [None]:
            tags = []
        
        # use tags_all as ultimate source of tags, unless tags is populated and tags_all is not (edge case)
        effective_tags = tags_all if tags_all else tags

        processed_tags = self.parse_tags(unwrap(effective_tags))

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

    def parse_tags(self, tags):
        missing = []
        invalid = []

        for tag in REQUIRED_TAGS:
            if tag not in tags:
                missing.append(tag)
                continue

            tag_value = unwrap(tags[tag])

            if is_empty(tag_value):
                missing.append(f"{tag} (empty)")
                continue

            if isinstance(tag_value, bool):
                tag_value = str(tag_value).lower()

            valid_tag_values = VALID_TAG_VALUES.get(tag, False)

            if valid_tag_values:
                if tag_value not in valid_tag_values:
                    invalid.append(
                        f"{tag}='{tag_value}' (valid: {', '.join(valid_tag_values)})"
                    )

        return {"missing": missing, "invalid": invalid}


check = RequiredTagsCheck()
