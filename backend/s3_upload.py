# s3_upload.py

import boto3
import uuid
import mimetypes
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ======= AWS CONFIGURATION FROM ENVIRONMENT =======
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION', 'ap-southeast-1')

# ======= SAFETY CHECK =======
if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME]):
    print("WARNING - AWS credentials not found in environment variables.")
    print("INFO - Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_S3_BUCKET_NAME in your .env file")
    # Don't exit, just disable S3 functionality
    s3_client = None
else:
    # ======= INITIALIZE S3 CLIENT =======
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        print("SUCCESS - S3 client initialized successfully")
    except Exception as e:
        print(f"ERROR - Failed to initialize S3 client: {e}")
        s3_client = None


def upload_file_to_s3(file_data, original_filename, content_type=None):
    """
    Uploads file to S3 and returns the file URL.
    Ensures proper content type for supported image formats.
    """
    try:
        extension = original_filename.split('.')[-1] if '.' in original_filename else 'jpg'
        unique_key = f"items/{uuid.uuid4()}.{extension.lower()}"

        # Guess and correct content type
        guessed_type, _ = mimetypes.guess_type(original_filename)
        content_type = content_type or guessed_type or 'image/jpeg'

        # Force correct content types for known extensions
        ext = extension.lower()
        if ext in ['jpg', 'jpeg']:
            content_type = 'image/jpeg'
        elif ext == 'png':
            content_type = 'image/png'
        elif ext == 'webp':
            content_type = 'image/webp'
        elif ext == 'gif':
            content_type = 'image/gif'
        else:
            content_type = 'application/octet-stream'

        # Upload to S3
        s3_client.put_object(
            Bucket=AWS_S3_BUCKET_NAME,
            Key=unique_key,
            Body=file_data,
            ContentType=content_type
        )

        file_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_key}"
        print(f"SUCCESS - File uploaded: {file_url}")
        return file_url

    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"ERROR - Credential Error: {e}")
        raise
    except ClientError as e:
        print(f"ERROR - S3 Error: {e}")
        raise
    except Exception as e:
        print(f"ERROR - Unexpected Error: {e}")
        raise


def test_s3_connection():
    """Test S3 connection by checking bucket access."""
    if s3_client is None:
        print("ERROR - S3 client not initialized")
        return False
    
    try:
        s3_client.head_bucket(Bucket=AWS_S3_BUCKET_NAME)
        print(f"SUCCESS - S3 Bucket accessible: {AWS_S3_BUCKET_NAME}")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '403':
            print(f"ERROR - S3 connection failed: Access denied to bucket '{AWS_S3_BUCKET_NAME}'")
            print("INFO - This usually means:")
            print("   - The bucket exists but your AWS user doesn't have permission")
            print("   - Check your IAM permissions for s3:GetBucketLocation and s3:ListBucket")
            print("   - Verify the bucket name is correct")
        elif error_code == '404':
            print(f"ERROR - S3 connection failed: Bucket '{AWS_S3_BUCKET_NAME}' not found")
            print("INFO - This usually means:")
            print("   - The bucket name is incorrect")
            print("   - The bucket is in a different region")
            print("   - The bucket doesn't exist")
        else:
            print(f"ERROR - S3 connection failed: {e}")
        print("WARNING - Will use local storage as fallback")
        return False
    except Exception as e:
        print(f"ERROR - S3 connection failed: {e}")
        print("WARNING - Will use local storage as fallback")
        return False


if __name__ == "__main__":
    test_s3_connection()
    # Test with a local image (optional)
    if os.path.exists("test.jpg"):
        with open("test.jpg", "rb") as f:
            data = f.read()
            url = upload_file_to_s3(data, "test.jpg")
            print(url)
    else:
        print("⚠️ No test.jpg file found to upload.")
