variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "race-photos"
}

variable "key_pair_name" {
  description = "Nome do key pair para EC2"
  type        = string
}