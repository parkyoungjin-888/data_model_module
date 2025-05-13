import importlib
import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Tuple


class ModelImporter:
    def __init__(self, s3_client, bucket: str = "datamodel", cash_dir: str = "/tmp/cached_model"):
        self.s3_client = s3_client
        self.bucket = bucket
        self.cash_dir = cash_dir
        os.makedirs(self.cash_dir, exist_ok=True)

    def _get_remote_model_version(self, file_name: str) -> str:
        response = self.s3_client.head_object(Bucket=self.bucket, Key=f"{file_name}.py")
        version = response.get('VersionId') if response else None
        return version

    def _get_cached_version(self, file_name: str) -> Optional[str]:
        version_file = os.path.join(self.cash_dir, f"{file_name}.version")
        if not os.path.exists(version_file):
            return None
        with open(version_file, 'r') as f:
            return f.read().strip()

    def _save_cached_version(self, file_name: str, version: str):
        version_file = os.path.join(self.cash_dir, f"{file_name}.version")
        with open(version_file, 'w') as f:
            f.write(version)

    def _download_model_from_s3(self, file_name: str, version: Optional[str] = None) -> Tuple[str, str]:
        local_path = os.path.join(self.cash_dir, f"{file_name}.py")
        current_version = self._get_remote_model_version(file_name)
        cached_version = self._get_cached_version(file_name)
        if version is None and cached_version == current_version:
            return local_path, cached_version
            
        extra_args = {}
        if version is not None:
            extra_args['VersionId'] = version
        elif current_version is not None:
            extra_args['VersionId'] = current_version

        try:
            self.s3_client.download_file(self.bucket, f"{file_name}.py", local_path, ExtraArgs=extra_args)
            self._save_cached_version(file_name, version or current_version)
            return local_path, version or current_version
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"Model file {file_name} not found in S3")
            raise

    def import_model(self, file_name: str, model_name: str, version: Optional[str] = None):
        try:
            model_path, model_version = self._download_model_from_s3(file_name, version)
            cache_dir = os.path.dirname(model_path)
            import sys
            if cache_dir not in sys.path:
                sys.path.append(cache_dir)
                
            module = importlib.import_module(file_name)
            return getattr(module, model_name)
        except Exception as e:
            raise ImportError(f"Failed to import model {model_name} from file {file_name}: {str(e)}")

    def list_model_versions(self, file_name: str) -> list:
        try:
            response = self.s3_client.list_object_versions(Bucket=self.bucket, Prefix=f"{file_name}.py")
            versions = []
            for version in response.get('Versions', []):
                version_body = {
                    'version_id': version['VersionId'],
                    'last_modified': version['LastModified'],
                    'size': version['Size']
                }
                versions.append(version_body)
            return versions
        except ClientError as e:
            raise Exception(f"Failed to list versions for file {file_name}: {str(e)}")
        

if __name__ == "__main__":
    from botocore.client import Config

    endpoint = "http://:9000"
    access_key = ""
    secret_key = ""
    s3 = boto3.client('s3',
                      endpoint_url=endpoint, 
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key,
                      config=Config(signature_version='s3v4'))
    model_importer = ModelImporter(s3, cash_dir='./temp/cash')
    model = model_importer.import_model("images_model", "Image")
    print(model)
