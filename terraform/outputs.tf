output "terraform_state_bucket" {
  description = "Name of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.bucket
}

output "aws_region" {
  description = "AWS region where resources are created"
  value       = var.region
}

output "github_actions_role_arn" {
  description = "ARN of the IAM role for GitHub Actions"
  value       = var.github_org != "" && var.github_repo != "" ? aws_iam_role.github_actions[0].arn : "Not created - GitHub variables not provided"
}

output "backend_ecr_repository_url" {
  description = "URL of the backend ECR repository"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
} 