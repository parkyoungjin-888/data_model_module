import importlib
import os
from botocore.exceptions import ClientError
from typing import Optional, Tuple


class ModelCacheManager:
    def __init__(self, s3_client, bucket: str, file: str, file_cache_dir: str = "./tmp/cached_model"):
        self.s3_client = s3_client
        self.bucket = bucket
        self.file = file
        self.file_cache_dir = file_cache_dir
        os.makedirs(self.file_cache_dir, exist_ok=True)
        self._model_cache = {}

    def _get_remote_model_version(self) -> str:
        response = self.s3_client.head_object(Bucket=self.bucket, Key=self.file)
        version = response.get('VersionId') if response else None
        return version

    def _get_cached_version(self) -> Optional[str]:
        version_file = os.path.join(self.file_cache_dir, f"{self.file}.version")
        if not os.path.exists(version_file):
            return None
        with open(version_file, 'r') as f:
            return f.read().strip()

    def _save_cached_version(self, version: str):
        version_file = os.path.join(self.file_cache_dir, f"{self.file}.version")
        with open(version_file, 'w') as f:
            f.write(version)

    def _download_model_from_s3(self, version: Optional[str] = None) -> Tuple[str, str]:
        local_path = os.path.join(self.file_cache_dir, self.file)
        remote_version = self._get_remote_model_version()
        cached_version = self._get_cached_version()
        if version is None and cached_version == remote_version:
            return local_path, cached_version
        
        extra_args = {}
        if version is not None:
            extra_args['VersionId'] = version
        elif remote_version is not None:
            extra_args['VersionId'] = remote_version

        try:
            self.s3_client.download_file(self.bucket, self.file, local_path, ExtraArgs=extra_args)
            self._save_cached_version(version or remote_version)
            return local_path, version or remote_version
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"Model file {self.file} not found in S3")
            raise

    def _load_model(self, model_name: str):
        local_path = os.path.join(self.file_cache_dir, self.file)
        self.download_model()

        try:
            cache_dir = os.path.dirname(local_path)
            import sys
            if cache_dir not in sys.path:
                sys.path.append(cache_dir)
            module_name = os.path.splitext(os.path.basename(self.file))[0]
            module = importlib.import_module(module_name)
            model_obj = getattr(module, model_name)
            self._model_cache[model_name] = model_obj
        except Exception as e:
            raise ImportError(f"Failed to load model {model_name} from file {self.file}: {str(e)}")

    def get_model(self, model_name: str):
        if model_name not in self._model_cache:
            self._load_model(model_name)
        return self._model_cache[model_name]

    def download_model(self, version: Optional[str] = None):
        self._download_model_from_s3(version)
        