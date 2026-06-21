output "api_endpoint" {
  description = "Base URL for the API Gateway HTTP API."
  value       = aws_apigatewayv2_api.http.api_endpoint
}

output "calculate_url" {
  description = "POST endpoint for calculator requests."
  value       = "${aws_apigatewayv2_api.http.api_endpoint}/calculate"
}

output "lambda_function_name" {
  description = "Created Lambda function name."
  value       = aws_lambda_function.agent.function_name
}

