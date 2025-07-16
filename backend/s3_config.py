# AWS S3 Configuration and Upload Service
import boto3
import uuid
import mimetypes
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import io

# AWS Configuration - Load from environment variables (SECURE)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'your_access_key_here')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'your_secret_key_here')
AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME', 'your_bucket_name_here')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')  # Default to us-east-1 if not specified

# Validation: Check if credentials are properly configured
if any(cred in ['your_access_key_here', 'your_secret_key_here', 'your_bucket_name_here'] 
       for cred in [AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME]):
    print("⚠️  WARNING: AWS credentials not configured!")
    print("Please set environment variables or update s3_config.py")
    print("Required: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME")

# Initialize S3 client
try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
except Exception as e:
    print(f"❌ Failed to initialize S3 client: {e}")
    s3_client = None

def upload_file_to_s3(file_data, original_filename, content_type=None):
    """
    Upload a file to S3 bucket and return the public URL
    
    Args:
        file_data: File content as bytes
        original_filename: Original filename
        content_type: MIME type of the file
    
    Returns:
        str: Public URL of the uploaded file
    """
    try:
        # Generate unique filename
        file_extension = original_filename.split('.')[-1] if '.' in original_filename else 'jpg'
        unique_filename = f"items/{uuid.uuid4()}.{file_extension}"
        
        # Determine content type
        if not content_type:
            content_type, _ = mimetypes.guess_type(original_filename)
            if not content_type:
                content_type = 'application/octet-stream'
        
        # Upload to S3 without ACL (bucket policy handles public access)
        s3_client.put_object(
            Bucket=AWS_S3_BUCKET_NAME,
            Key=unique_filename,
            Body=file_data,
            ContentType=content_type
            # Removed ACL='public-read' since bucket doesn't support ACLs
        )
        
        # Generate public URL
        file_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"
        
        print(f"✅ File uploaded successfully: {file_url}")
        return file_url
        
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"❌ AWS credentials error: {e}")
        raise Exception("AWS credentials not configured properly")
    
    except ClientError as e:
        print(f"❌ S3 upload error: {e}")
        raise Exception(f"Failed to upload to S3: {e}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise Exception(f"File upload failed: {e}")

def test_s3_connection():
    """Test if S3 connection and credentials are working"""
    try:
        # Try to list bucket contents (just to test connection)
        s3_client.head_bucket(Bucket=AWS_S3_BUCKET_NAME)
        print(f"✅ S3 connection successful! Bucket: {AWS_S3_BUCKET_NAME}")
        return True
    except Exception as e:
        print(f"❌ S3 connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test S3 connection when file is run directly
    test_s3_connection() 