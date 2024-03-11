from dotenv import load_dotenv
import environ
import base64
import boto3
import os

# Environment variables
env = environ.Env()
environ.Env.read_env()

class S3Client:
    _instance = None
    bucket_name = env("SILVERCARE_AWS_S3_BUCKET_NAME")
    directory = env("SILVERCARE_AWS_S3_BUCKET_SUBDIR")
    
    def __init__(self):
        pass

    def get_instance():
        """
        Singleton pattern/function to get the S3 client instance.
        Returns:
            boto3.client: The S3 client instance.
        """
        if S3Client._instance is None:
            S3Client._instance = boto3.client(
                "s3",
                aws_access_key_id=env("SILVERCARE_AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=env("SILVERCARE_AWS_SECRET_ACCESS_KEY"),
                region_name=env("SILVERCARE_AWS_REGION_NAME"),
            )
        return S3Client._instance

    def check_image_exists(category, id):
        """
        Checks if an image exists in the S3 bucket.
        Args:
            file_name (str): The name of the file to be checked.
        Returns:
            bool: True if the file exists, False otherwise.
        """
        try:
            S3Client._instance.head_object(Bucket=S3Client.bucket_name, Key=f"{S3Client.directory}/{category}/{id}")
            return True
        except Exception as e:
            print(e)
            return False
  
    def download_image(category, id):
        """
        Downloads a file from the S3 bucket.
        Args:
            file_name (str): The name of the file to be downloaded.
        Returns:
            bytes: The contents of the file.
        """
        if not id:
            return None
        return S3Client._instance.get_object(Bucket=S3Client.bucket_name, Key=f"{S3Client.directory}/{category}/{id}")["Body"].read().decode('utf-8')

    def download_image_encode_base64(category, id):
        """
        Downloads a file from the S3 bucket and returns it as a base64 string.
        Args:
            file_name (str): The name of the file to be downloaded.
        Returns:
            str: The contents of the file as a base64 string.
        """
        return base64.b64encode(S3Client._instance.get_object(Bucket=S3Client.bucket_name, Key=f"{S3Client.directory}/{category}/{id}")["Body"].read()).decode('utf-8')

    def upload_image(category, id, file):
        """
        Uploads a file to the S3 bucket.
        Args:
            file_name (str): The name of the file to be uploaded.
            file (bytes): The contents of the file.
        """
        S3Client._instance.put_object(Bucket=S3Client.bucket_name, Key=f"{S3Client.directory}/{category}/{id}", Body=file)

    def upload_image_encode_base64(category, id, file):
        """
        Uploads a file to the S3 bucket from a base64 string.
        Args:
            file_name (str): The name of the file to be uploaded.
            file (str): The contents of the file as a base64 string.
        """
        S3Client._instance.put_object(Bucket=S3Client.bucket_name, Key=f"{S3Client.directory}/{category}/{id}", Body=base64.b64encode(file.read()))
        