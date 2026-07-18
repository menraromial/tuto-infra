# Exercice final du bloc 5, partie Terraform : un bucket S3 sur LocalStack.
# Tout est identique à du vrai AWS, sauf le bloc "endpoints" du provider.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.region

  # LocalStack accepte n'importe quels identifiants : rien de secret ici.
  access_key = "test"
  secret_key = "test"

  # Tout ce bloc dit au provider de parler à LocalStack plutôt qu'à AWS :
  s3_use_path_style           = true # http://localhost:4566/bucket au lieu de http://bucket.localhost
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    s3 = "http://localhost:4566"
  }
}

resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project}-data-lake"

  tags = {
    Project   = var.project
    ManagedBy = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Un premier objet, pour vérifier que le bucket est utilisable :
resource "aws_s3_object" "readme" {
  bucket  = aws_s3_bucket.data_lake.id
  key     = "README.txt"
  content = "Bucket ${aws_s3_bucket.data_lake.bucket} provisionné par Terraform.\n"
}
