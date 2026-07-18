variable "project" {
  description = "Préfixe des ressources créées"
  type        = string
  default     = "tuto"
}

variable "region" {
  description = "Région AWS simulée par LocalStack"
  type        = string
  default     = "eu-west-1"
}
