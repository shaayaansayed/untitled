# Get GitHub's OIDC thumbprint
data "tls_certificate" "github" {
  url = "https://token.actions.githubusercontent.com/.well-known/openid-configuration"
}

# Create OIDC Identity Provider
resource "aws_iam_openid_connect_provider" "github_actions" {
  count = var.github_org != "" && var.github_repo != "" ? 1 : 0
  
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.github.certificates[0].sha1_fingerprint]

  tags = {
    Name    = "GitHub Actions OIDC Provider"
    Purpose = "Allow GitHub Actions to assume AWS roles"
  }
}

# IAM role for GitHub Actions
resource "aws_iam_role" "github_actions" {
  count = var.github_org != "" && var.github_repo != "" ? 1 : 0
  
  name = "github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github_actions[0].arn
        }
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/${var.github_repo}:*"
          }
        }
      }
    ]
  })

  tags = {
    Name    = "GitHub Actions Deployment Role"
    Purpose = "Role for GitHub Actions to deploy infrastructure"
  }
}

# Permissions for GitHub Actions role
resource "aws_iam_role_policy" "github_actions" {
  count = var.github_org != "" && var.github_repo != "" ? 1 : 0
  
  name = "github-actions-policy"
  role = aws_iam_role.github_actions[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Terraform state management
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.terraform_state.arn,
          "${aws_s3_bucket.terraform_state.arn}/*"
        ]
      },
      # Infrastructure permissions (we'll expand this as needed)
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "ecs:*",
          "elasticloadbalancing:*",
          "logs:*",
          "ecr:*",
          "iam:GetRole",
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:PassRole",
          "iam:ListAttachedRolePolicies",
          "iam:ListRolePolicies"
        ]
        Resource = "*"
      }
    ]
  })
} 