variable "region" {
  description = "AWS region where to create resources"
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "Name of your project (will be used in resource names)"
  type        = string
  
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "github_org" {
  description = "GitHub organization or username"
  type        = string
  default     = ""
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = ""
} 