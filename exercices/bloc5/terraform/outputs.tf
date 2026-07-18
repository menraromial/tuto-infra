output "bucket_name" {
  description = "Nom du bucket créé"
  value       = aws_s3_bucket.data_lake.bucket
}

output "bucket_arn" {
  description = "ARN du bucket (format identique au vrai AWS)"
  value       = aws_s3_bucket.data_lake.arn
}
