terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  # You need replace it with profile which contains real AWS credentials, region
  profile = "codeforpoznan"
}

resource "aws_cloudwatch_log_group" "alinka-codebuild-pr" {
  name = "alinka-codebuild-pr"

  tags = {
    Created = "Terraform"
  }
}

# Role trust relationship
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "my_alinka_codebuild_pr_role" {
  name               = "MyAlinka-codebuild-pr-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json

  tags = {
    Created = "Terraform"
  }
}

data "aws_iam_policy_document" "codebuild_policy" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:GetBucketAcl",
      "s3:GetBucketLocation"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "codebuild:CreateReportGroup",
      "codebuild:CreateReport",
      "codebuild:UpdateReport",
      "codebuild:BatchPutTestCases",
      "codebuild:BatchPutCodeCoverages"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "alinka_codebuild_pr_policy" {
  name   = "Alinka-codebuild-pr-policy"
  role   = aws_iam_role.my_alinka_codebuild_pr_role.name
  policy = data.aws_iam_policy_document.codebuild_policy.json
}

resource "aws_codebuild_project" "alinka_codebuild_pr_config" {
  name          = "Alinka-pr-build"
  description   = "Run test and linters on pull request"
  build_timeout = 5
  service_role  = aws_iam_role.my_alinka_codebuild_pr_role.arn

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/standard:6.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = "true"
  }

  logs_config {
    cloudwatch_logs {
      group_name = "alinka-codebuild-pr"
    }
  }

  source {
    type            = "GITHUB"
    location        = "https://github.com/CodeForPoznan/alinka-pyside.git"
    git_clone_depth = 0
    buildspec       = "etc/buildspec.yml"
  }

  source_version = "refs/pull/*/head"

  tags = {
    Created = "Terraform"
  }
}

resource "aws_codebuild_webhook" "alinka_codebuild_pr_webhook" {
  project_name = aws_codebuild_project.alinka_codebuild_pr_config.name
  build_type   = "BUILD"
  filter_group {
    filter {
      type    = "EVENT"
      pattern = "PULL_REQUEST_CREATED,PULL_REQUEST_UPDATED,PULL_REQUEST_REOPENED,PULL_REQUEST_MERGED"
    }
  }
}
