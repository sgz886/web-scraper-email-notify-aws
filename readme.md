# Web Scraper with Email Notifications(AWS)

## Overview
An AWS Lambda-based web scraper that monitors file updates on a website. When new files are detected, it sends email notifications via AWS SES (Simple Email Service). The application uses DynamoDB to store and compare file listings between runs.

Key Features:
- Automated web scraping with BeautifulSoup
- File change detection and tracking
- Email notifications for new files
- AWS Lambda deployment
- DynamoDB storage
- Logging with email reports


## Prerequisites
- Python 3.9+
- AWS Account with:
  - Lambda access
  - DynamoDB table
  - SES verified emails
  - IAM role with appropriate permissions
- AWS CLI configured locally

### AWS Requirements
- Lambda Function
- DynamoDB Table
- SES Configuration:
  - Verified sender email
  - Verified recipient emails
  - Appropriate SES sending limits
- IAM Role with policies for:
  - Lambda execution
  - DynamoDB access
  - SES sending
  - CloudWatch logging

## Local Development

### Setup
1. Clone the repository:
2. Create virtual environment:
    ```bash
    python -m venv .venv
    ```
3. Activate virtual environment:
    ```bash
    .venv\Scripts\activate # Windows
    source .venv/bin/activate # MacOS/Linux
    ```
4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Create `.env` file:

    following the `.env.example` file

### Run the project
```bash
python src/main.py
```
### Running Tests
The project uses pytest for testing. All test files are located in the `tests/` directory.
```bash
pytest
```
## AWS Lambda Deployment
1. Create deployment package:
    ```bash
    make_lambda_package.cmd # Windows
    ```

2. Upload `crawler_for_lambda.zip` to AWS Lambda

3. Configure Lambda Environment Variables:
   - Set all environment variables from `.env` file in Lambda configuration

4. Configure runtime settings:
   - Runtime: Python 3.9+
   - handler: main.lambda_handler

5. Set up Lambda trigger:
   - Configure EventBridge for scheduled execution



## File Structure
```shell
├── src/
│ ├── data/ # Database handling
│ ├── notification/ # Email notification
│ ├── scraper/ # Web scraping
│ ├── service/ # Business logic
│ ├── util/ # Utilities
│ └── main.py # Entry point
├── tests/ # Test files
├── .env.example # Example environment variables
├── setup.py # Package setup configuration
├── pyproject.toml # Project metadata and tool configs
├── requirements.txt # Development dependencies
└── requirements-prod.txt # Production dependencies
```
