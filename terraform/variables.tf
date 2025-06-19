variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "untitled"
}

variable "environment" {
  description = "Environment (e.g., dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "container_port" {
  description = "Port on which the container runs"
  type        = number
  default     = 8000
}

variable "db_name" {
  description = "Name of the database"
  type        = string
  default     = "app"
}

variable "db_username" {
  description = "Username for the database"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Password for the database"
  type        = string
  sensitive   = true
  default     = "password"
}