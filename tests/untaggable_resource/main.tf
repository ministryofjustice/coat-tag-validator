terraform {
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
}

provider "aws" {
    region = "eu-west-2"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_requesting_account_id  = true
    access_key                  = "mock"
    secret_key                  = "mock"
}

provider "aws" {
    region = "us-east-1"
    alias  = "secondary_region"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_requesting_account_id  = true
    access_key                  = "mock"
    secret_key                  = "mock"
}

resource "aws_s3_bucket" "test" {
    bucket = "test-bucket-compliant"

    tags = {
        business-unit = "HMPPS"
        application   = "test-app"
        owner         = "test@example.com"
        is-production = "false"
        service-area  = "testing"
    }
}

resource "aws_s3_bucket" "test_two" {
    provider = aws.secondary_region
    bucket = "test-two-bucket-compliant"

    tags = {
        business-unit = "HMPPS"
        application   = "test-app"
        owner         = "test@example.com"
        is-production = "false"
        service-area  = "testing"
    }
}

# Multi region access point is untaggable
resource "aws_s3control_multi_region_access_point" "test" {
  details {
    name = "example"

    region {
      bucket = aws_s3_bucket.test.id
    }

    region {
      bucket = aws_s3_bucket.test_two.id
    }
  }
}