import boto3
import io
from PIL import Image

# Create an S3 client to interact with AWS S3
s3 = boto3.client('s3')
# Destination bucket is stored in an environment variable
# This makes the function flexible without hardcoding bucket names
DEST_BUCKET = os.environ["DESTINATION_BUCKET"]

def lambda_handler(event, context):
    try:
        # Extract source bucket name and image key from the Step Functions input
        source_bucket = event['bucket']
        image_key = event['key']
        
        # Download the original image from S3 (Source S3)
        obj = s3.get_object(Bucket=source_bucket, Key=image_key)
        # Load image using Pillow (PIL)
        image = Image.open(io.BytesIO(obj['Body'].read()))
        
        # Resize image while keeping aspect ratio (720x720)
        image.thumbnail((720, 720))

        # Save resized image to an in-memory stream
        output_stream = io.BytesIO()
        image_format = image.format or 'JPEG' # Use original format or default to JPEG
        image.save(output_stream, format=image_format)
        output_stream.seek(0)  # Reset pointer to beginning of the stream

        # Create a new key name for the resized image
        dest_key = f"resized-{image_key}"
        # Upload resized image to the destination S3 bucket
        s3.put_object(Bucket=DEST_BUCKET, Key=dest_key, Body=output_stream)

        # Return success result to Step Functions
        return {
            "status": "success",
            "image_key": dest_key
        }
        # Return error details to Step Functions
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }