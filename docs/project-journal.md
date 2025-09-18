# Serverless API Project Journal

## Week 1

#### Day 1 (September 8, 2025) - Plan: Project Setup
- **Tasks Completed**: Defined endpoints (GET /weather for mock weather data, POST /calculate for math operations). Sketched architecture (API Gateway, Lambda, DynamoDB). Outlined 2-week schedule (Plan-Build-Test-Deploy-Operate).
- **Notes/Learnings**: Serverless architecture enables scalability with minimal management. Used README.md to document requirements (AWS SAM, Python 3.13, Git). Focused on learning Infrastructure as Code (IaC) and CI/CD.
- **Challenges**: Refreshed understanding of serverless concepts (e.g., Lambda event triggers).
- **Code Snippets**:
  - README.md excerpt:
    ```markdown
    # Serverless API Project
    - Endpoints: GET /weather, POST /calculate
    - Tools: AWS SAM, Python 3.13, DynamoDB
    ```
- **Next Steps**: Set up tools and environment (Day 2).

#### Day 2 (September 9, 2025) - Plan: Tools & Setup
- **Tasks Completed**: Installed AWS CLI, SAM CLI, Python 3.13. Configured AWS credentials (IAM user: serverless-dev-user with AdministratorAccess). Created DynamoDB table `apiData` via CLI. Tested put/get-item with mock weather data.
- **Notes/Learnings**: AWS CLI manages credentials securely. SAM CLI simplifies serverless deployments. DynamoDB on-demand billing fits free tier. JSON escaping in Bash is critical for CLI commands.
- **Challenges**: Fixed JSON escaping in put-item command. Manually verified IAM setup.
- **Code Snippets**:
  - Create table:
    ```bash
    aws dynamodb create-table --table-name apiData --attribute-definitions AttributeName=pk,AttributeType=S AttributeName=timestamp,AttributeType=S --key-schema AttributeName=pk,KeyType=HASH AttributeName=timestamp,KeyType=RANGE --billing-mode PAY_PER_REQUEST
    ```
  - Put item:
    ```bash
    aws dynamodb put-item --table-name apiData --item '{"pk": {"S": "weather#London"}, "timestamp": {"S": "2025-09-14T12:00:00Z"}, "type": {"S": "weather"}, "temperature": {"N": "20"}, "humidity": {"N": "60"}, "description": {"S": "Partly cloudy"}}'
    ```
  - Output: `{}` (success).
- **Next Steps**: Build Lambda functions (Day 3).

#### Day 3 (September 14, 2025) - Build: Lambda Functions
- **Tasks Completed**: Created `src/` folder and `template.yaml` for SAM. Wrote `weather.py` handler with mock data, Boto3 for DynamoDB put, and real-time timestamp. Built with `sam build`, tested locally with `sam local invoke` using `events/weather-event.json`.
- **Notes/Learnings**: SAM template defines serverless resources (IaC). Handlers process API Gateway events (query params). Local invoke skips real DynamoDB but validates logic. Used Python 3.13 runtime.
- **Challenges**: Fixed SAM CLI recognition in Bash with alias. Resolved Python runtime mismatch (updated to 3.13). Debugged JSON event formatting.
- **Code Snippets**:
  - template.yaml excerpt:
    ```yaml
    Resources:
      WeatherFunction:
        Type: AWS::Serverless::Function
        Properties:
          CodeUri: ./src
          Handler: weather.handler
          Runtime: python3.13
          Environment:
            Variables:
              TABLE_NAME: apiData
          Policies: AmazonDynamoDBFullAccess
    ```
  - weather.py (key part):
    ```python
    import json
    import boto3
    import os
    from datetime import datetime, UTC

    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ['TABLE_NAME']

    def handler(event, context):
        city = event.get('queryStringParameters', {}).get('city', 'London')
        mock_weather = {'city': city, 'temperature': 20, 'humidity': 60, 'description': 'Partly cloudy'}
        timestamp = datetime.now(UTC).isoformat() + 'Z'
    ```
  - event.json:
    ```json
    {"queryStringParameters": {"city": "London"}}
    ```
  - Invoke output: `{"statusCode": 200, "body": "{\"city\": \"London\", \"temperature\": 20, \"humidity\": 60, \"description\": \"Partly cloudy\"}"}`.
- **Next Steps**: Integrate API Gateway, add calc function (Day 4).

#### Day 4 (September 15, 2025) - Build: API Gateway Integration
- **Tasks Completed**: Added API Gateway Events for GET /weather in `template.yaml`. Created `calc.py` for POST /calculate (handles add/subtract/multiply, stores in DynamoDB). Built with `sam build`, tested locally with `sam local start-api` and curl.
- **Notes/Learnings**: API Gateway routes requests to Lambdas via Events. curl tests validated JSON responses (200 for valid, 400 for errors). Local tests skip real DynamoDB writes but confirm handler logic.
- **Challenges**: Learned curl POST syntax with `-d` for JSON. Fixed YAML indentation errors. Installed Docker for SAM local testing.
- **Code Snippets**:
  - template.yaml API event:
    ```yaml
    Events:
      WeatherApi:
        Type: Api
        Properties:
          Path: /weather
          Method: get
    ```
  - calc.py (key part):
    ```python
    import json
    import boto3
    import os
    from datetime import datetime, UTC
    from uuid import uuid4

    def handler(event, context):
        body = json.loads(event.get('body', '{}'))
        operation = body.get('operation')
        numbers = body.get('numbers', [])
        if operation not in ['add', 'subtract', 'multiply']:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Unsupported operation'})}
        result = numbers[0]
        for num in numbers[1:]:
            if operation == 'add': result += num
            elif operation == 'subtract': result -= num
            elif operation == 'multiply': result *= num
    ```
  - curl tests:
    ```bash
    curl http://127.0.0.1:3000/weather?city=London
    curl -X POST -H "Content-Type: application/json" -d '{"operation": "add", "numbers": [2, 3]}' http://127.0.0.1:3000/calculate
    ```
  - Outputs: Weather: `{"city": "London", "temperature": 20, "humidity": 60, "description": "Partly cloudy"}`, Calculate: `{"result": 5, "operation": "add", "id": "calc#<uuid>", "timestamp": "..."}`.
- **Next Steps**: Refine DynamoDB, test live writes (Day 5).

#### Day 5 (September 16, 2025) - Build: Refine DynamoDB Integration
- **Tasks Completed**: Added try/except error handling to `weather.py` and `calc.py` for DynamoDB writes. Created `env.json` for local testing. Tested live DynamoDB writes with `sam local start-api --env-vars env.json`. Verified writes in `apiData` table via AWS Console/CLI.
- **Notes/Learnings**: try/except prevents crashes on DynamoDB errors. env.json sets `TABLE_NAME` for local tests with live AWS resources. curl syntax critical for POST. Free tier covers writes.
- **Challenges**: Fixed missing `json` import in `calc.py` (500 error). Created `env.json` to resolve TABLE_NAME errors.
- **Code Snippets**:
  - calc.py error handling:
    ```python
    from botocore.exceptions import ClientError
    try:
        table.put_item(Item=item)
    except ClientError as e:
        return {'statusCode': 500, 'body': json.dumps({'error': f'DynamoDB error: {str(e)}'})}
    ```
  - env.json:
    ```json
    {"WeatherFunction": {"TABLE_NAME": "apiData"}, "CalcFunction": {"TABLE_NAME": "apiData"}}
    ```
  - curl tests: Same as Day 4.
  - DynamoDB scan: `[{"pk": "weather#London", "timestamp": "..."}, {"pk": "calc#<uuid>", "result": 5, ...}]`.
- **Next Steps**: Unit and integration tests (Day 6).

#### Day 6 (September 16, 2025) - Test: Unit and Integration Tests
- **Tasks Completed**: Wrote unit tests for `weather.py` and `calc.py` using pytest and moto (`mock_aws`). Fixed `TABLE_NAME` KeyError with `os.environ`. Ran integration tests with `sam local start-api --env-vars env.json`, verified live DynamoDB writes with curl and AWS Console.
- **Notes/Learnings**: Unit tests isolate handler logic; integration tests use real DynamoDB. moto mocks AWS services locally. curl confirmed end-to-end flow (request → Lambda → DB).
- **Challenges**: Fixed moto import issues (`mock_aws` vs. `mock_dynamodb`). Added `os.environ['TABLE_NAME']` to tests. Resolved src module import with PYTHONPATH.
- **Code Snippets**:
  - test_weather.py:
    ```python
    import pytest
    import boto3
    from moto import mock_aws
    import json
    import os
    os.environ['TABLE_NAME'] = 'apiData'
    from src.weather import handler

    @mock_aws
    def test_weather_handler():
        # Mock DynamoDB, test handler
    ```
  - curl tests: Same as Day 4.
  - Outputs: Weather: `{"city": "London", ...}`, Calculate: `{"result": 5, ...}`.
  - pytest: `2 passed in X.XXs`.
- **Next Steps**: Performance and security tests (Day 7).

## Week 2

#### Day 7 (September 17, 2025) - Test: Performance & Security
- **Tasks Completed**: Ran Locust load test (5 users, 60s, 50 requests, 0% fails) on GET /weather, POST /calculate. Checked dependencies with `pip-audit`, verified IAM permissions, tested input validation (400 for invalid inputs).
- **Notes/Learnings**: Locust showed high local latency (~3-9s) due to Docker/SAM cold starts. pip-audit ensured no vulnerable dependencies. IAM user had AdministratorAccess. Validation rejects invalid operations.
- **Challenges**: Switched to Locust after npm oversight (Artillery). Mastered curl `-H` for JSON POST.
- **Code Snippets**:
  - locustfile.py:
    ```python
    from locust import HttpUser, task, between
    class ApiUser(HttpUser):
        wait_time = between(1, 3)
        @task
        def get_weather(self):
            self.client.get("/weather?city=London")
    ```
  - Locust command:
    ```bash
    locust -f locustfile.py --host=http://127.0.0.1:3000 --headless -u 5 -r 5 -t 60s
    ```
  - Output: Aggregated 50 reqs, 0% fails, avg 3876ms, median 3100ms.
  - Validation test:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"operation": "divide"}' http://127.0.0.1:3000/calculate
    ```
  - Output: `{"error": "Unsupported operation"}`.
- **Next Steps**: Deploy to staging (Day 8).

#### Day 8 (September 17, 2025) - Deploy: Staging Setup
- **Tasks Completed**: Deployed staging stack (`serverless-api-staging`, il-central-1) with `sam deploy --guided`. Set up GitHub Actions CI/CD (`deploy.yml`) with Python 3.13, S3 bucket. Tested live API with curl, verified DynamoDB writes. Fixed `--resolve-s3` error in CI/CD.
- **Notes/Learnings**: SAM creates CloudFormation stacks (Lambdas, API Gateway, roles). CI/CD automates deployments on push. Retrieved API URL via console/CLI. Live API faster (~100-500ms vs. local).
- **Challenges**: Fixed `--resolve-s3` vs. `--s3-bucket` conflict in CI/CD. Retrieved URL via `aws apigateway get-rest-apis`.
- **Code Snippets**:
  - deploy.yml:
    ```yaml
    - run: sam deploy --stack-name serverless-api-staging --region il-central-1 --s3-bucket aws-sam-cli-managed-default-samclisourcebucket-cfc57lijl025 --no-confirm-changeset --no-fail-on-empty-changeset --capabilities CAPABILITY_IAM
    ```
  - curl tests:
    ```bash
    curl https://<staging-id>.execute-api.il-central-1.amazonaws.com/Prod/weather?city=London
    curl -X POST -H "Content-Type: application/json" -d '{"operation": "add", "numbers": [2, 3]}' https://<staging-id>.execute-api.il-central-1.amazonaws.com/Prod/calculate
    ```
  - Outputs: Weather: `{"city": "London", "temperature": 20, ...}`, Calculate: `{"result": 5, ...}`.
  - DynamoDB scan: `[{"pk": "weather#London", "timestamp": "..."}, {"pk": "calc#<uuid>", ...}]`.
- **Next Steps**: Production deployment, CI/CD multi-env (Day 9).

#### Day 9 (September 17, 2025) - Deploy: Production Setup
- **Tasks Completed**: Deployed production stack (`serverless-api-prod`, il-central-1) with `sam deploy`. Updated CI/CD (`deploy.yml`) for staging/prod jobs with `needs: deploy-staging`. Tested prod API with curl, verified writes. Fixed commit message typo.
- **Notes/Learnings**: Staging tests changes before prod deployment. Prod uses separate API Gateway URL but shares `apiData` table. CI/CD ensures safe updates with sequential jobs.
- **Challenges**: Fixed CI/CD job names (deploy-staging vs. deploy-prod). Clarified staging vs. production purposes (testing vs. live use).
- **Code Snippets**:
  - deploy.yml:
    ```yaml
    jobs:
      deploy-staging:
        # ...
      deploy-prod:
        needs: deploy-staging
        # ...
    ```
  - curl tests:
    ```bash
    curl https://<prod-id>.execute-api.il-central-1.amazonaws.com/Prod/weather?city=London
    curl -X POST -H "Content-Type: application/json" -d '{"operation": "add", "numbers": [2, 3]}' https://<prod-id>.execute-api.il-central-1.amazonaws.com/Prod/calculate
    ```
  - Outputs: Weather: `{"city": "London", "temperature": 20, ...}`, Calculate: `{"result": 5, ...}`.
  - DynamoDB scan: `[{"pk": "weather#London", "timestamp": "..."}, {"pk": "calc#<uuid>", ...}]`.
- **Next Steps**: Monitoring and optimization (Day 10).

#### Day 10 (September 17, 2025) - Operate: Monitoring & Optimization
- **Tasks Completed**: Added CloudWatch metrics (`WeatherLatency`, `CalcLatency`) to `weather.py` and `calc.py`. Created `WeatherLatencyHigh` alarm (>500ms) in AWS Console. Increased Lambda memory to 256MB in `template.yaml`, redeployed. Analyzed metrics: ~160ms avg (graph), ~245-257ms log duration.
- **Notes/Learnings**: CloudWatch logs show cold starts (~400-500ms init). Custom metric (~160ms) slightly lower than Duration (~245ms) due to Lambda overhead—normal. 256MB memory reduces latency. Free tier covers usage.
- **Challenges**: Understood ~85ms metric vs. log duration difference (normal). Navigated CloudWatch console for alarm setup.
- **Code Snippets**:
  - weather.py metric:
    ```python
    cloudwatch = boto3.client('cloudwatch')
    latency = (datetime.now(UTC) - start_time).total_seconds() * 1000
    cloudwatch.put_metric_data(
        Namespace='ServerlessAPI',
        MetricData=[{'MetricName': 'WeatherLatency', 'Value': latency, 'Unit': 'Milliseconds'}]
    )
    ```
  - CloudWatch CLI:
    ```bash
    aws cloudwatch get-metric-statistics --namespace ServerlessAPI --metric-name WeatherLatency --start-time 2025-09-17T00:00:00Z --end-time 2025-09-17T23:59:59Z --period 60 --statistics Average --region il-central-1
    ```
  - Outputs: Weather: Duration 245.33ms, Billed 777ms, Init 531.21ms; Graph avg ~160ms. Calc: Duration 257.22ms, Billed 721ms, Init 463.12ms.
- **Next Steps**: Project complete, optional cleanup.

## Project Summary
- **Outcome**: Built a serverless REST API with AWS SAM, Python 3.13, DynamoDB, and GitHub Actions CI/CD. Deployed to staging (`serverless-api-staging`) and production (`serverless-api-prod`) in `il-central-1`. Tested with pytest (unit), Locust (load), and curl (integration). Monitored with CloudWatch (latency ~160ms, alarm >500ms). Documented for portfolio.
- **Repo**: [Replace with your GitHub repo URL].