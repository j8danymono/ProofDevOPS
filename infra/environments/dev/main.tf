terraform {
  backend "s3" {
    bucket         = "devops-123-tf-state"
    key            = "dev/app/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "devops-123-tf-lock"
  }
}

module "app" {
  source       = "../../modules/app"
  project_name = var.project_name
  environment  = var.environment
  region       = var.region
  s3_bucket    = var.s3_bucket
}

output "api_endpoint" {
  value = module.app.api_endpoint
}
