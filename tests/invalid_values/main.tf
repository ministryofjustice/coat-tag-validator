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

resource "aws_s3_bucket" "test" {
    bucket = "test-bucket-compliant"

    tags = {
        business-unit = "HQ"
        application   = "test-app"
        owner         = "test@example.com"
        is-production = "lalala"
        service-area  = "testing"
    }
}

resource "aws_s3_bucket" "test1" {
    bucket = "test-bucket-compliant1"

    tags = {
        business-unit = "HQ"
        application   = "test-app"
        owner         = "test@example.com"
        is-production = "lalala"
        service-area  = "testing"
    }
}

resource "aws_s3_bucket" "test2" {
    bucket = "test-bucket-compliant2"

    tags = {
        business-unit = "HQ"
        application   = "test-app"
        owner         = "test@example.com"
        is-production = "lalala"
        service-area  = "testing"
    }
}

resource "aws_s3_bucket" "test3" {
    bucket = "test-bucket-compliant3"

    tags = {
        business-unit = "HQ"
        application   = "test-app"
        owner         = "test@example.com"
        is-production = "lalala"
        service-area  = "testing"
    }
}

resource "aws_s3_bucket" "test4" {
    bucket = "test-bucket-compliant4"

    tags = {
        business-unit = "HQ"
        application   = "test-app"
        owner         = "test@example.com"
        is-production = "lalala"
        service-area  = "testing"
    }
}