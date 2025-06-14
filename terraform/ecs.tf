# Get default VPC (every AWS account has one)
data "aws_vpc" "default" {
  default = true
}

# Get default subnets
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ECR repository for backend
resource "aws_ecr_repository" "backend" {
  name = "backend"

  tags = {
    Name = "backend-repo"
  }
}

# Security group for backend (allow port 8000 from internet)
resource "aws_security_group" "backend" {
  name_prefix = "backend-"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Allow from internet
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "backend-sg"
  }
}

# ECS cluster
resource "aws_ecs_cluster" "main" {
  name = "main-cluster"

  tags = {
    Name = "main-cluster"
  }
}

# Task execution role
resource "aws_iam_role" "ecs_execution_role" {
  name = "ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Backend task definition
resource "aws_ecs_task_definition" "backend" {
  family                   = "backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = "backend"
      # Use nginx as a placeholder until we push our FastAPI image
      image = "nginx:alpine"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      
      essential = true
    }
  ])

  tags = {
    Name = "backend-task"
  }

  # This prevents Terraform from reverting the image when we update via GitHub Actions
  lifecycle {
    ignore_changes = [container_definitions]
  }
}

# ECS service (public IP, no load balancer)
resource "aws_ecs_service" "backend" {
  name            = "backend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.backend.id]
    assign_public_ip = true  # Give it a public IP directly
  }

  tags = {
    Name = "backend-service"
  }
} 