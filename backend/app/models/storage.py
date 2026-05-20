from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# 与 ROOT_FOLDER_ID 错开，便于人工识别种子数据
LOCAL_BACKEND_ID = "00000000-0000-4000-8000-000000000002"
S3_BACKEND_ID = "00000000-0000-4000-8000-000000000003"


class StorageBackend(Base):
    """逻辑存储端；endpoint/bucket/密钥以本表为准（与正式环境一致）。"""

    __tablename__ = "storage_backends"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, default="default")
    provider: Mapped[str] = mapped_column(
        String(32), nullable=False, default="local"
    )  # local | minio | aws | generic_s3
    endpoint_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    region: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    use_path_style: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default_bucket: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    access_key_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    secret_access_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    sse_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    secret_ref: Mapped[str] = mapped_column(String(255), nullable=False, default="db")
    is_readonly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    blobs: Mapped[list["Blob"]] = relationship(back_populates="backend")


class Blob(Base):
    """物理对象（字节在驱动侧）；nodes.blob_id 指向本表。"""

    __tablename__ = "blobs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    storage_backend_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("storage_backends.id", ondelete="RESTRICT"),
        nullable=False,
    )
    bucket: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    object_key: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    etag: Mapped[str | None] = mapped_column(String(128), nullable=True)
    version_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    storage_class: Mapped[str | None] = mapped_column(String(32), nullable=True)
    refcount: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    backend: Mapped["StorageBackend"] = relationship(back_populates="blobs")
