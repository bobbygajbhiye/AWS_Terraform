# LangGraph Calculator Agent on AWS Lambda

This sample repo contains a small LangGraph calculator agent, an AWS Lambda/API Gateway deployment defined in Terraform, a Streamlit front end, and a GitHub Actions workflow that deploys on pushes to `main`.

## What It Creates

- `lambda_src/`: Python Lambda handler plus a LangGraph calculator agent.
- `frontend/streamlit_app.py`: Streamlit UI for local or deployed calculator calls.
- `terraform/`: AWS Lambda, CloudWatch logs, IAM role, and API Gateway HTTP API.
- `.github/workflows/deploy.yml`: GitHub Actions workflow using AWS OIDC and Terraform.

## Local Run

Install app dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the Streamlit app:

```powershell
streamlit run frontend/streamlit_app.py
```

By default the UI runs the local LangGraph agent. To call the deployed Lambda API, set `LAMBDA_API_URL` to the Terraform `calculate_url` output.

## Build Lambda Package

On Windows:

```powershell
.\scripts\build_lambda_package.ps1
```

On Linux/macOS/GitHub Actions:

```bash
bash scripts/build_lambda_package.sh
```

The build creates `build/lambda_package`, which Terraform zips with the `archive_file` data source.

## Deploy With Terraform

```powershell
.\scripts\build_lambda_package.ps1
terraform -chdir=terraform init -backend-config="bucket=YOUR_TF_STATE_BUCKET" -backend-config="key=langgraph-calculator-agent/terraform.tfstate" -backend-config="region=us-east-1" -backend-config="encrypt=true" -backend-config="use_lockfile=true"
terraform -chdir=terraform plan -var="aws_region=us-east-1"
terraform -chdir=terraform apply -var="aws_region=us-east-1"
terraform -chdir=terraform output calculate_url
```

## GitHub Actions Setup

1. Push this folder to a GitHub repository on the `main` branch.
2. Create an S3 bucket for Terraform state and enable bucket versioning. The workflow uses S3 lockfiles, so it does not need DynamoDB.
3. In GitHub, add repository variables named `AWS_REGION`, `TF_STATE_BUCKET`, and optionally `TF_STATE_KEY`.
4. In GitHub, add a repository secret named `AWS_ROLE_TO_ASSUME`.
5. Create an AWS IAM role that trusts GitHub OIDC for your repository. The examples in `docs/` show a trust policy and a starter permissions policy.
6. Push to `main` or run the workflow manually from the Actions tab.

The workflow deploys automatically on `push` to `main` and also supports `workflow_dispatch`. The Terraform state bucket must exist before the first run.

## API Contract

POST the calculator input to the API:

```json
{
  "question": "12 * (7 + 5)"
}
```

The Lambda responds with:

```json
{
  "input": "12 * (7 + 5)",
  "expression": "12 * (7 + 5)",
  "result": "144",
  "answer": "12 * (7 + 5) = 144"
}
```

