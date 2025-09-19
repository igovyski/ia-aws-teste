terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 Bucket para fotos
resource "aws_s3_bucket" "photos" {
  bucket = "${var.project_name}-photos-${random_string.bucket_suffix.result}"

  tags = {
    Name = "race-photos-bucket"
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# EC2 Instance
resource "aws_instance" "web" {
  ami           = "ami-0c02fb55956c7d316" # Amazon Linux 2
  instance_type = "t3.micro"
  key_name      = var.key_pair_name

  user_data = base64encode(file("${path.module}/user_data.sh"))

  tags = {
    Name = "race-photos-web"
  }
}