provider "aws" {
  region = "us-west-2"
}

resource "aws_ecs_cluster" "fastapi_cluster" {
  name = "fastapi-cluster"
}

resource "aws_ecr_repository" "fastapi_repo" {
  name = "fastapi-repo"
}

resource "aws_lb" "fastapi_lb" {
  name               = "fastapi-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.fastapi_sg.id]
  subnets            = [aws_subnet.public_subnet.id]
}

resource "aws_lb_target_group" "fastapi_tg" {
  name     = "fastapi-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 5
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "fastapi_listener" {
  load_balancer_arn = aws_lb.fastapi_lb.arn
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fastapi_tg.arn
  }
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
}

resource "aws_security_group" "fastapi_sg" {
  name        = "fastapi-sg"
  description = "Security group for FastAPI"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}