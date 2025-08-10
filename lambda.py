import json
import boto3
import base64
import os

# Create the boto3 clients outside of the handler for better performance
s3 = boto3.client('s3')
sagemaker_runtime = boto3.client("sagemaker-runtime")

# ==============================================================================
# Lambda Function 1: Data Serialization
# ==============================================================================
def serializeImageData_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket = event['s3_bucket']
    
    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket, key, "/tmp/image.png")
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Pass the data back to the Step Function
    print("Event:", event.keys())
    
    # The return format is crucial for Step Functions
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
# (This is the simplified boto3 version)
# ==============================================================================
# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2025-08-09-11-26-07-217" 

def imageClassifier_handler(event, context):
    """A function to invoke the SageMaker endpoint for image classification"""

    # The event from the previous Lambda is nested in the 'body'
    event_body = event['body']
    image_data = event_body['image_data']

    # Decode the base64 image data
    image = base64.b64decode(image_data)
    
    # Make a prediction by invoking the endpoint using boto3
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=ENDPOINT,
        ContentType="image/png",
        Body=image
    )
    
    # Get the inferences from the response
    inferences = response["Body"].read().decode('utf-8')

    # We return the data back to the Step Function
    event_body["inferences"] = inferences
    
    return {
        'statusCode': 200,
        'body': json.dumps(event_body)
    }


# ==============================================================================
# Lambda Function 3: Filter Low Confidence
# ==============================================================================
# Define your confidence threshold
THRESHOLD = 0.93

def filterLowConfidence_handler(event, context):
    """A function to filter out inferences below a threshold"""

    # The event from the previous Lambda is a JSON string
    event_body = json.loads(event['body'])
    inferences_str = event_body['inferences']
    inferences = json.loads(inferences_str)
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(inferences) > THRESHOLD
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise Exception("THRESHOLD_CONFIDENCE_NOT_MET")
    
    return {
        'statusCode': 200,
        'body': json.dumps(event_body)
    }