from __future__ import annotations

import io
import pathlib

from PIL import Image
from starlette.concurrency import run_in_threadpool


THUMBNAIL_SIZE = 200


async def thumbnail_from_path(path: pathlib.Path, size: int = THUMBNAIL_SIZE) -> bytes:
    def _resize() -> bytes:
        img = Image.open(path)
        img.thumbnail((size, size))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80)
        return buf.getvalue()

    return await run_in_threadpool(_resize)


async def thumbnail_from_bytes(data: bytes, size: int = THUMBNAIL_SIZE) -> bytes:
    def _resize() -> bytes:
        img = Image.open(io.BytesIO(data))
        img.thumbnail((size, size))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80)
        return buf.getvalue()

    return await run_in_threadpool(_resize)
