from __future__ import annotations

from app.core.config import Settings
from app.models.storage import StorageBackend
from app.services.storage_drivers.local import LocalStorageDriver
from app.services.storage_drivers.protocol import StorageDriver
from app.services.storage_drivers.s3 import S3StorageDriver


def get_driver(backend: StorageBackend, settings: Settings) -> StorageDriver:
    if backend.provider == "local":
        return LocalStorageDriver(settings)
    if backend.provider in ("minio", "aws", "generic_s3", "aliyun"):
        return S3StorageDriver(backend, settings)
    raise ValueError(f"unsupported storage provider: {backend.provider}")
