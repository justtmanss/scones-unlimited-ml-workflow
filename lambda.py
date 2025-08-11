# ==============================================================================
# Lambda Function 1: Data Serialization
# ==============================================================================
import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    key = event['s3_key']
    bucket = event['s3_bucket']
    
    s3.download_file(bucket, key, "/tmp/image.png")
    
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

# ==============================================================================
# Lambda Function 2: Image Classification
# ==============================================================================
import json
import boto3
import base64

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2025-08-09-11-26-07-217" 

sagemaker_runtime = boto3.client("sagemaker-runtime")

def lambda_handler(event, context):
    """A function to invoke the SageMaker endpoint for image classification"""

    event_body = event['body']
    image_data = event_body['image_data']

    image = base64.b64decode(image_data)
    
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=ENDPOINT,
        ContentType="image/png",
        Body=image
    )
    
    inferences = response["Body"].read().decode('utf-8')

    event_body["inferences"] = inferences
    
    return {
        'statusCode': 200,
        'body': json.dumps(event_body)
    }

# ==============================================================================
# Lambda Function 3: Filter Low Confidence
# ==============================================================================
import json

# Define your confidence threshold
THRESHOLD = 0.93

def lambda_handler(event, context):
    """A function to filter out inferences below a threshold"""

    event_body = json.loads(event['body'])
    inferences_str = event_body['inferences']
    inferences = json.loads(inferences_str)
    
    meets_threshold = max(inferences) > THRESHOLD
    
    if meets_threshold:
        pass
    else:
        raise Exception("THRESHOLD_CONFIDENCE_NOT_MET")
    
    return {
        'statusCode': 200,
        'body': json.dumps(event_body)
    }