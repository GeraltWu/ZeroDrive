from __future__ import annotations

import re

_SEGMENT_RE = re.compile(r"[^/\x00-\x1f]+")


class PathValidationError(Exception):
    pass


class PathNotFoundError(Exception):
    def __init__(self, segment: str, resolved_prefix: str) -> None:
        self.segment = segment
        self.resolved_prefix = resolved_prefix
        super().__init__(segment)


def normalize_path(path: str) -> list[str]:
    raw = (path or "").strip()
    if not raw:
        raise PathValidationError("path 不能为空")
    if not raw.startswith("/"):
        raise PathValidationError("path 必须以 / 开头，如 / 或 /图片/奶龙")
    # 根目录
    if raw == "/":
        return []
    if "\\" in path or ".." in raw:
        raise PathValidationError("path 非法")
    segments: list[str] = []
    for part in raw.lstrip("/").split("/"):
        part = part.strip()
        if not part:
            continue
        if part == "..":
            raise PathValidationError("path 非法")
        if len(part) > 512:
            raise PathValidationError("路径段过长")
        if not _SEGMENT_RE.fullmatch(part):
            raise PathValidationError("路径段含非法字符")
        segments.append(part)
    if not segments:
        raise PathValidationError("path 不能为空")
    return segments
