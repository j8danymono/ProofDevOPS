terraform {
  required_version = ">= 1.6.0"

  backend "s3" {
    bucket         = "devops-test-123-tf-state"
    key            = "dev/app/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "devops-test-123-tf-lock"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# IAM ROLE FOR LAMBDA

resource "aws_iam_role" "lambda_exec" {
  name = "${var.project_name}-lambda-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# DynamoDB permissions
resource "aws_iam_role_policy_attachment" "lambda_dynamodb" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

# DYNAMODB TABLE FOR ITEMS

resource "aws_dynamodb_table" "items" {
  name         = "${var.project_name}-items"
  billing_mode = "PAY_PER_REQUEST"

  hash_key = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

# LAMBDA FUNCTION

resource "aws_lambda_function" "api" {
  function_name = "${var.project_name}-api"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  timeout       = 10

  filename         = "${path.module}/../../build/lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/../../build/lambda.zip")

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.items.name
    }
  }
}

# API GATEWAY (HTTP API)

resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.project_name}-http-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_credentials = false
    allow_headers     = ["*"]
    allow_methods     = ["GET", "POST", "OPTIONS"]
    allow_origins     = ["*"]
    max_age           = 300
  }
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

# ROUTES (PROFESIONAL)

# GET /health
resource "aws_apigatewayv2_route" "health" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# GET /items
resource "aws_apigatewayv2_route" "get_items" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /items"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# POST /items
resource "aws_apigatewayv2_route" "post_items" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /items"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# STAGE

resource "aws_apigatewayv2_stage" "dev" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "dev"
  auto_deploy = true

  lifecycle {
    create_before_destroy = true
  }
}

# PERMISSIONS FOR API → LAMBDA

resource "aws_lambda_permission" "allow_apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# OUTPUTS

output "api_endpoint" {
  value = "${aws_apigatewayv2_api.http_api.api_endpoint}/${aws_apigatewayv2_stage.dev.name}"
}
