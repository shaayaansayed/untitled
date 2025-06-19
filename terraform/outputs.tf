output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.app_repo.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.app.name
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.app.name
}

output "frontend_s3_bucket_name" {
  description = "Name of the S3 bucket for frontend"
  value       = aws_s3_bucket.frontend.bucket
}

output "frontend_s3_bucket_website_endpoint" {
  description = "Website endpoint of the S3 bucket"
  value       = aws_s3_bucket_website_configuration.frontend.website_endpoint
}

output "frontend_cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "frontend_cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.frontend.id
}

output "frontend_url" {
  description = "Frontend URL (via CloudFront)"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "files_s3_bucket_name" {
  description = "Name of the S3 bucket for files"
  value       = aws_s3_bucket.files.bucket
}

output "files_s3_bucket_arn" {
  description = "ARN of the S3 bucket for files"
  value       = aws_s3_bucket.files.arn
}

output "files_s3_bucket_domain_name" {
  description = "Domain name of the S3 bucket for files"
  value       = aws_s3_bucket.files.bucket_domain_name
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "backend_cloudfront_domain_name" {
  description = "Domain name of the backend CloudFront distribution"
  value       = aws_cloudfront_distribution.backend.domain_name
}

output "backend_cloudfront_distribution_id" {
  description = "ID of the backend CloudFront distribution"
  value       = aws_cloudfront_distribution.backend.id
}

output "backend_url" {
  description = "Backend URL (via CloudFront)"
  value       = "https://${aws_cloudfront_distribution.backend.domain_name}"
}