from __future__ import annotations

import pathlib
from typing import Any, BinaryIO

from fastapi import UploadFile

from app.core.config import Settings
from app.services import storage as local_storage


class LocalStorageDriver:
    provider = "local"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def is_filesystem(self) -> bool:
        return True

    def filesystem_path(self, object_key: str) -> pathlib.Path:
        return local_storage.abs_path(object_key)

    async def put_upload_file(self, bucket: str, object_key: str, upload: UploadFile) -> tuple[int, str | None]:
        _ = bucket
        size = await local_storage.save_upload_from_uploadfile(object_key, upload)
        return size, None

    def delete_object(self, bucket: str, object_key: str) -> None:
        _ = bucket
        local_storage.delete_blob(object_key)

    def get_object_stream(
        self, bucket: str, object_key: str, range_header: str | None
    ) -> tuple[BinaryIO, dict[str, Any]]:
        _ = bucket, range_header
        path = local_storage.abs_path(object_key)
        f = open(path, "rb")
        try:
            length = path.stat().st_size
        except OSError:
            f.close()
            raise
        return f, {"ContentLength": length, "ETag": None, "Status": 200}
