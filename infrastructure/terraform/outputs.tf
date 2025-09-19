output "s3_bucket_name" {
  description = "Nome do bucket S3"
  value       = aws_s3_bucket.photos.bucket
}

output "ec2_public_ip" {
  description = "IP público da instância EC2"
  value       = aws_instance.web.public_ip
}

output "ec2_public_dns" {
  description = "DNS público da instância EC2"
  value       = aws_instance.web.public_dns
}