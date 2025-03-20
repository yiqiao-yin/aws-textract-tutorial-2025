# AWS Lambda and API Gateway Tutorial

This tutorial covers setting up a Lambda function that uses AWS Textract to analyze documents. It also includes creating an inline policy for the IAM role, configuring an API Gateway, and invoking the API using various programming languages.

## Setting up the Lambda Function

The following Python code defines a Lambda function to process documents using AWS Textract. It handles errors and logs necessary information for debugging.

```python
import json
import base64
import logging
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get the boto3 client
try:
    textract_client = boto3.client('textract')
    logger.info("Successfully initialized Textract client.")
except BotoCoreError as e:
    logger.error(f"Failed to initialize Textract client: {e}")
    raise

def lambda_handler(event, context):
    """
    Lambda function to process REST API requests for Textract document analysis.
    Supports ANY HTTP method.
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        if 'body' not in event or not event['body']:
            raise ValueError("Missing request body")

        request_body = json.loads(event['body'])

        image = None
        if 'image' in request_body:
            image_bytes = request_body['image'].encode('utf-8')
            img_b64decoded = base64.b64decode(image_bytes)
            image = {'Bytes': img_b64decoded}
        elif 'S3Object' in request_body:
            image = {'S3Object': {
                'Bucket': request_body['S3Object']['Bucket'],
                'Name': request_body['S3Object']['Name']
            }}
        else:
            raise ValueError("Invalid input: Provide 'image' as base64 or 'S3Object'")

        response = textract_client.detect_document_text(Document=image)
        blocks = response.get('Blocks', [])
        logger.info("Successfully processed document with Textract.")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"Blocks": blocks})
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"Error": str(e)})
        }
```

## Inline Policy for IAM Role

Create an inline policy for the Lambda function's IAM role to allow it to call Textract:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "textract:DetectDocumentText",
            "Resource": "*",
            "Effect": "Allow",
            "Sid": "DetectDocumentText"
        }
    ]
}
```

## Setting Up API Gateway

Follow these steps to set up an API Gateway:

1. **Create a new API** in the AWS Management Console under API Gateway.
2. **Create a new resource** under your API, typically using the '/' as the root resource.
3. **Create a new method** (e.g., POST) under the newly created resource.
4. **Set up the integration request** to invoke your Lambda function.
5. **Deploy the API** by creating a new deployment stage.

## Invoking the API

Here are examples of how to invoke the API using different programming languages:

### Curl

```bash
curl -X POST https://your-api-id.execute-api.region.amazonaws.com/stage \
     -H "Content-Type: application/json" \
     -d '{"image":"base64-encoded-image-data"}'
```

### Python

```python
import requests

url = "https://your-api-id.execute-api.region.amazonaws.com/stage"
data = {"image": "base64-encoded-image-data"}
response = requests.post(url, json=data)
print(response.text)
```

### Node.js

```javascript
const axios = require('axios');

let url = "https://your-api-id.execute-api.region.amazonaws.com/stage";
let data = {
  image: "base64-encoded-image-data"
};

axios.post(url, data)
  .then(response => console.log(response.data))
  .catch(error => console.log(error));
```

### TypeScript (.tsx)

```typescript
import axios from 'axios';

const url: string = "https://your-api-id.execute-api.region.amazonaws.com/stage";
const data: any = { image: "base64-encoded-image-data" };

axios.post(url, data)
  .then(response => console.log(response.data))
  .catch(error => console.error(error));
```
