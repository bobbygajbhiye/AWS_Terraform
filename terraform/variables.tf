variable "aws_region" {
  description = "AWS region for Lambda and API Gateway."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix for created AWS resources."
  type        = string
  default     = "langgraph-calculator-agent"
}

variable "lambda_memory_size" {
  description = "Lambda memory size in MB."
  type        = number
  default     = 512
}

variable "lambda_timeout" {
  description = "Lambda timeout in seconds."
  type        = number
  default     = 20
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days."
  type        = number
  default     = 14
}

