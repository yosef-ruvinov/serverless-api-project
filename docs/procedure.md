# Serverless API End-to-End Procedure

This document outlines the end-to-end procedure to run the serverless API project (GET /weather, POST /calculate) from a clean environment, ensuring no conflicts with existing AWS resources or processes. It uses AWS SAM, Python 3.13, DynamoDB, and GitHub Actions, as built over 10 days.

## Prerequisites

- **Tools**: AWS CLI, SAM CLI, Python 3.13, Git, Bash (Git Bash on Windows).
- **AWS Account**: Configured with IAM user (serverless-dev-user, AdministratorAccess).
- **GitHub Repo**: Cloned from your repository (contains `src/`, `template.yaml`, `deploy.yml`).
- **Environment**: Windows (MINGW64) at `~/Desktop/devops/projects/serverless-api-project`.

## Procedure

### 1. Validate Clean Environment

Ensure no conflicting AWS resources or processes exist to avoid errors.

```bash
# Check for running SAM processes (local API)
ps aux | grep sam
# If SAM running (e.g., sam local start-api), kill: Ctrl+C in terminal or kill <pid>

# Check for existing CloudFormation stacks
aws cloudformation list-stacks --region il-central-1 --query 'StackSummaries[?StackName==`serverless-api-staging` || StackName==`serverless-api-prod`]'
# Expected: [] (empty). If stacks exist, delete:
aws cloudformation delete-stack --stack-name serverless-api-staging --region il-central-1
aws cloudformation delete-stack --stack-name serverless-api-prod --region il-central-1
aws cloudformation wait stack-delete-complete --stack-name serverless-api-staging --region il-central-1
aws cloudformation wait stack-delete-complete --stack-name serverless-api-prod --region il-central-1

# Check for DynamoDB table (apiData exists, keep it)
aws dynamodb describe-table --table-name apiData --region il-central-1
# If "TableNotFoundException", create table:
aws dynamodb create-table --table-name apiData --attribute-definitions AttributeName=pk,AttributeType=S AttributeName=timestamp,AttributeType=S --key-schema AttributeName=pk,KeyType=HASH AttributeName=timestamp,KeyType=RANGE --billing-mode PAY_PER_REQUEST --region il-central-1
aws dynamodb wait table-exists --table-name apiData --region il-central-1

# Verify S3 bucket (for SAM artifacts)
aws s3 ls s3://aws-sam-cli-managed-default-samclisourcebucket-cfc57lijl025 --region il-central-1
# If "NoSuchBucket", let SAM create one during deploy (--resolve-s3)

# Verify AWS credentials
aws sts get-caller-identity
# Expected: Shows serverless-dev-user
```

### 2. Clone and Set Up Project

```bash
# Clone repo (replace with your GitHub URL)
git clone https://github.com/yosef-ruvinov/serverless-api-project.git serverless-api-project
cd serverless-api-project

# Install dependencies
pip install boto3 pytest moto[dynamodb] locust
```

### 3. Run Unit Tests

Validate Lambda logic locally with pytest and moto.

```bash
PYTHONPATH=$(pwd) pytest tests/
# Expected: "2 passed" (test_weather.py, test_calc.py)
```

### 4. Deploy to Production

Deploy the API to AWS (production stack).

```bash
sam build
sam deploy --stack-name serverless-api-prod --region il-central-1 --resolve-s3 --no-confirm-changeset --no-fail-on-empty-changeset --capabilities CAPABILITY_IAM
# Expected: "Successfully created/updated stack - serverless-api-prod"
```

### 5. Get API Gateway URL

```bash
aws apigateway get-rest-apis --region il-central-1 --query 'items[?contains(name, `serverless-api-prod`)].{id:id}'
# Construct URL: https://<id>.execute-api.il-central-1.amazonaws.com/Prod/
```

### 6. Test Live API

```bash
# GET /weather
curl "https://<id>.execute-api.il-central-1.amazonaws.com/Prod/weather?city=London"
# Expected: {"city": "London", "temperature": 20, "humidity": 60, "description": "Partly cloudy", "timestamp": "..."}

# POST /calculate
curl -X POST -H "Content-Type: application/json" -d '{"operation": "add", "numbers": [2, 3]}' "https://<id>.execute-api.il-central-1.amazonaws.com/Prod/calculate"
# Expected: {"result": 5, "operation": "add", "id": "calc#<uuid>", "timestamp": "..."}

# Error test
curl -X POST -H "Content-Type: application/json" -d '{"operation": "divide"}' "https://<id>.execute-api.il-central-1.amazonaws.com/Prod/calculate"
# Expected: {"error": "Unsupported operation"}
```

### 7. Verify DynamoDB Writes

```bash
aws dynamodb scan --table-name apiData --region il-central-1 --query 'Items[?pk.S==`weather#London` || starts_with(pk.S, `calc#`)].{pk:pk.S,timestamp:timestamp.S}'
# Expected: Items like {"pk": "weather#London", "timestamp": "..."}, {"pk": "calc#<uuid>", "timestamp": "..."}
```

### 8. Check CloudWatch Metrics and Alarms

```bash
# Metrics
aws cloudwatch get-metric-statistics --namespace ServerlessAPI --metric-name WeatherLatency --start-time 2025-09-18T00:00:00Z --end-time 2025-09-18T23:59:59Z --period 60 --statistics Average --region il-central-1
# Expected: Average ~160-260ms

# Alarms
aws cloudwatch describe-alarms --alarm-names WeatherLatencyHigh --region il-central-1
# Expected: State "OK" (if <500ms)
```

### Functionality Flow

1. Client sends HTTP request (GET /weather or POST /calculate) to API Gateway.
2. API Gateway routes to Lambda (WeatherFunction or CalcFunction).
3. Lambda processes request (mock weather or math calc), writes to DynamoDB (`apiData`), logs latency to CloudWatch.
4. Response returns to client (~160-260ms).
5. CloudWatch monitors latency; alarms trigger if >500ms.

## Notes

- **Costs**: Free tier (~$0 for low usage).
- **Demo**: Show GitHub repo, run curl commands, check DynamoDB/CloudWatch in AWS Console.
- **Troubleshooting**: Check CloudWatch logs (/aws/lambda/WeatherFunction, CalcFunction) for errors.
