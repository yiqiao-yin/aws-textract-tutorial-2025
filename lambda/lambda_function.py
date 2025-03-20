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

        # Ensure event has a body
        if 'body' not in event or not event['body']:
            raise ValueError("Missing request body")

        request_body = json.loads(event['body'])

        # Determine document source
        image = None
        if 'image' in request_body:
            try:
                image_bytes = request_body['image'].encode('utf-8')
                img_b64decoded = base64.b64decode(image_bytes)
                image = {'Bytes': img_b64decoded}
            except Exception as e:
                logger.error(f"Error decoding base64 image: {e}")
                raise ValueError("Invalid base64 image encoding")

        elif 'S3Object' in request_body:
            try:
                image = {'S3Object': {
                    'Bucket': request_body['S3Object']['Bucket'],
                    'Name': request_body['S3Object']['Name']
                }}
            except KeyError as e:
                logger.error(f"Missing key in S3Object structure: {e}")
                raise ValueError("Invalid S3Object structure, required: 'Bucket' and 'Name'")

        else:
            raise ValueError("Invalid input: Provide 'image' as base64 or 'S3Object' with bucket and name")

        # Call Amazon Textract
        try:
            response = textract_client.detect_document_text(Document=image)
            blocks = response.get('Blocks', [])
            logger.info("Successfully processed document with Textract.")
        except ClientError as e:
            logger.error(f"Textract client error: {e.response['Error']['Message']}")
            raise ValueError("Error processing document with Textract")
        except Exception as e:
            logger.error(f"Unexpected error calling Textract: {e}")
            raise ValueError("Unexpected error occurred while processing document")

        # Successful response
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"Blocks": blocks})
        }

    except ValueError as e:
        logger.error(f"Input validation error: {e}")
        return error_response(400, "ValueError", str(e))

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return error_response(500, "InternalServerError", "An internal error occurred. Check logs for details.")


def error_response(status_code, error_type, message):
    """Helper function to format error response."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "Error": error_type,
            "ErrorMessage": message
        })
    }