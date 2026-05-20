from __future__ import annotations

import asyncio
import os
import pathlib
import tempfile
from typing import Any, BinaryIO, Optional

import boto3
from botocore.client import Config
from fastapi import UploadFile

from app.models.storage import StorageBackend


def _resolve_s3_credentials(backend: StorageBackend) -> tuple[str | None, str | None]:
    """库中优先；否则走 AWS 默认链（如 EC2 实例角色，不传 static key）。"""
    ak = (backend.access_key_id or "").strip() or None
    sk = (backend.secret_access_key or "").strip() or None
    if ak and sk:
        return ak, sk
    env_ak = (os.environ.get("AWS_ACCESS_KEY_ID") or "").strip() or None
    env_sk = (os.environ.get("AWS_SECRET_ACCESS_KEY") or "").strip() or None
    return env_ak, env_sk


def _s3_client(backend: StorageBackend):
    ak, sk = _resolve_s3_credentials(backend)
    kwargs: dict[str, Any] = {
        "service_name": "s3",
        "region_name": (backend.region or "us-east-1").strip() or "us-east-1",
        "config": Config(
            signature_version="s3v4",
            s3={"addressing_style": "path" if backend.use_path_style else "auto"},
        ),
    }
    if backend.endpoint_url and str(backend.endpoint_url).strip():
        kwargs["endpoint_url"] = str(backend.endpoint_url).strip()
    if ak and sk:
        kwargs["aws_access_key_id"] = ak
        kwargs["aws_secret_access_key"] = sk
    return boto3.client(**kwargs)


class S3StorageDriver:
    def __init__(self, backend: StorageBackend, _settings: Optional[object] = None) -> None:
        self._backend = backend
        self._client = _s3_client(backend)

    @property
    def provider(self) -> str:
        return self._backend.provider

    def is_filesystem(self) -> bool:
        return False

    def filesystem_path(self, object_key: str) -> pathlib.Path:
        raise NotImplementedError("S3 driver has no local filesystem path")

    def _default_bucket(self, bucket: str) -> str:
        b = (bucket or "").strip() or (self._backend.default_bucket or "").strip()
        if not b:
            raise ValueError("S3 bucket 未配置：请在 storage_backends.default_bucket 中设置")
        return b

    async def put_upload_file(self, bucket: str, object_key: str, upload: UploadFile) -> tuple[int, str | None]:
        b = self._default_bucket(bucket)
        tmp_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".upload") as tmp:
                tmp_path = tmp.name
                total = 0
                while True:
                    chunk = await upload.read(1024 * 1024)
                    if not chunk:
                        break
                    tmp.write(chunk)
                    total += len(chunk)
            extra: dict[str, Any] = {}
            if (self._backend.sse_mode or "").strip().lower() == "aes256":
                extra["ServerSideEncryption"] = "AES256"
            upload_extra = extra if extra else None

            def _upload() -> str | None:
                if upload_extra:
                    self._client.upload_file(
                        tmp_path,
                        b,
                        object_key,
                        ExtraArgs=upload_extra,
                    )
                else:
                    self._client.upload_file(tmp_path, b, object_key)
                head = self._client.head_object(Bucket=b, Key=object_key)
                return head.get("ETag", "").strip('"') if head.get("ETag") else None

            etag = await asyncio.to_thread(_upload)
            return total, etag
        finally:
            if tmp_path and os.path.isfile(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    def delete_object(self, bucket: str, object_key: str) -> None:
        b = self._default_bucket(bucket)
        self._client.delete_object(Bucket=b, Key=object_key)

    def get_object_stream(
        self, bucket: str, object_key: str, range_header: str | None
    ) -> tuple[BinaryIO, dict[str, Any]]:
        b = self._default_bucket(bucket)
        kwargs: dict[str, Any] = {"Bucket": b, "Key": object_key}
        if range_header:
            kwargs["Range"] = range_header
        resp = self._client.get_object(**kwargs)
        body = resp["Body"]
        length = resp.get("ContentLength")
        meta: dict[str, Any] = {
            "ContentLength": length,
            "ETag": (resp.get("ETag") or "").strip('"') or None,
            "Status": 206 if resp.get("ContentRange") else 200,
        }
        if resp.get("ContentRange"):
            meta["ContentRange"] = resp["ContentRange"]
        return body, meta

    def download_object_to_path(self, bucket: str, object_key: str, dest_path: str) -> None:
        b = self._default_bucket(bucket)
        self._client.download_file(b, object_key, dest_path)
