from __future__ import annotations

import pathlib
from typing import Any, BinaryIO, Protocol

from fastapi import UploadFile


class StorageDriver(Protocol):
    """S3 与本地文件统一的写入/读取/删除抽象。"""

    @property
    def provider(self) -> str: ...

    def is_filesystem(self) -> bool:
        """为 True 时可用 filesystem_path + FileResponse（含 Range）。"""

    def filesystem_path(self, object_key: str) -> pathlib.Path:
        """仅 is_filesystem 时有效。"""

    async def put_upload_file(self, bucket: str, object_key: str, upload: UploadFile) -> tuple[int, str | None]:
        """流式写入对象；返回 (size_bytes, etag)。"""

    def delete_object(self, bucket: str, object_key: str) -> None: ...

    def get_object_stream(
        self, bucket: str, object_key: str, range_header: str | None
    ) -> tuple[BinaryIO, dict[str, Any]]:
        """返回 (可读流, 响应元数据 dict 含 ContentLength/ContentRange/ETag/Status 等)。"""
        ...
