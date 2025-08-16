import os
import logging
from typing import Optional, Tuple, List, Dict

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class R2Storage:
    """S3-compatible client for Cloudflare R2."""

    def __init__(self) -> None:
        bucket = os.getenv("R2_BUCKET_NAME") or os.getenv("S3_BUCKET_NAME")
        endpoint = os.getenv("R2_ENDPOINT") or os.getenv("S3_ENDPOINT")
        access_key = os.getenv("R2_ACCESS_KEY_ID") or os.getenv("S3_ACCESS_KEY_ID")
        secret_key = os.getenv("R2_SECRET_ACCESS_KEY") or os.getenv("S3_SECRET_ACCESS_KEY")
        region = os.getenv("R2_REGION") or os.getenv("S3_REGION") or "auto"

        if not (bucket and endpoint and access_key and secret_key):
            raise RuntimeError("R2 storage not configured: set R2_BUCKET_NAME, R2_ENDPOINT, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY")

        self.bucket = bucket
        # Use path-style addressing for R2
        self.s3 = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=Config(signature_version="s3v4"),
        )
        self.public_base = os.getenv("R2_PUBLIC_URL") or os.getenv("S3_PUBLIC_URL")

    def upload_bytes(self, key: str, data: bytes, content_type: Optional[str] = None) -> None:
        extra: Dict[str, str] = {}
        if content_type:
            extra["ContentType"] = content_type
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=data, **extra)

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            return self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            logger.error(f"Failed to presign URL for {key}: {e}")
            raise

    def generate_presigned_put_url(self, key: str, content_type: Optional[str] = None, expires_in: int = 3600) -> str:
        params = {"Bucket": self.bucket, "Key": key}
        if content_type:
            params["ContentType"] = content_type
        try:
            return self.s3.generate_presigned_url(
                "put_object",
                Params=params,
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            logger.error(f"Failed to presign PUT URL for {key}: {e}")
            raise

    def get_bytes(self, key: str) -> bytes:
        obj = self.s3.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read()

    def list_with_prefix(self, prefix: str) -> List[str]:
        keys: List[str] = []
        continuation_token = None
        while True:
            kwargs = {"Bucket": self.bucket, "Prefix": prefix}
            if continuation_token:
                kwargs["ContinuationToken"] = continuation_token
            resp = self.s3.list_objects_v2(**kwargs)
            for item in resp.get("Contents", []):
                keys.append(item["Key"])
            if resp.get("IsTruncated"):
                continuation_token = resp.get("NextContinuationToken")
            else:
                break
        return keys

    def build_public_url(self, key: str) -> Optional[str]:
        if not self.public_base:
            return None
        base = self.public_base.rstrip("/")
        return f"{base}/{key}"


_r2_singleton: Optional[R2Storage] = None


def get_r2_storage() -> R2Storage:
    global _r2_singleton
    if _r2_singleton is None:
        _r2_singleton = R2Storage()
    return _r2_singleton
