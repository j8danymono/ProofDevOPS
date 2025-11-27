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
  project_name = "devops-123"
  environment  = "dev"
  region       = "us-east-1"
}

output "api_endpoint" {
  value = module.app.api_endpoint
}
