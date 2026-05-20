from __future__ import annotations

import json
import pathlib
import subprocess
from typing import Any


def _to_float(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def extract_media_meta(file_path: pathlib.Path, mime_type: str | None = None) -> dict[str, Any] | None:
    """
    用 ffprobe 提取媒体元数据。
    失败时返回 None，不阻塞上传流程。
    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(file_path),
    ]
    try:
        # Windows 上 text=True 会按系统默认编码（常见 gbk）解码，可能导致 UnicodeDecodeError。
        # 这里按 bytes 捕获，再用 utf-8 容错解码，避免子进程读取线程崩溃。
        proc = subprocess.run(cmd, capture_output=True, timeout=8, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None

    stdout = (proc.stdout or b"").decode("utf-8", errors="replace")
    if proc.returncode != 0 or not stdout.strip():
        return None

    try:
        raw = json.loads(stdout)
    except json.JSONDecodeError:
        return None

    fmt = raw.get("format") if isinstance(raw.get("format"), dict) else {}
    streams = raw.get("streams") if isinstance(raw.get("streams"), list) else []
    duration = _to_float(fmt.get("duration"))
    bit_rate = _to_float(fmt.get("bit_rate"))

    meta: dict[str, Any] = {
        "source": "ffprobe",
        "mime_type": mime_type,
        "duration_seconds": duration,
        "bit_rate": int(bit_rate) if bit_rate is not None else None,
        "format_name": fmt.get("format_name"),
        "size_bytes": int(fmt["size"]) if str(fmt.get("size", "")).isdigit() else None,
    }

    audio_stream = next((s for s in streams if isinstance(s, dict) and s.get("codec_type") == "audio"), None)

    # 过滤音频附件封面流（ffprobe 会把它标成 video + attached_pic=1）
    def is_real_video_stream(s: dict[str, Any]) -> bool:
        if s.get("codec_type") != "video":
            return False
        disposition = s.get("disposition")
        if isinstance(disposition, dict) and disposition.get("attached_pic") == 1:
            return False
        return True

    video_stream = next(
        (s for s in streams if isinstance(s, dict) and is_real_video_stream(s)),
        None,
    )

    mime_lower = (mime_type or "").lower()
    prefer_audio = mime_lower.startswith("audio/")
    prefer_video = mime_lower.startswith("video/")

    if video_stream and (prefer_video or not prefer_audio):
        meta["kind"] = "video"
        meta["width"] = video_stream.get("width")
        meta["height"] = video_stream.get("height")
        meta["video_codec"] = video_stream.get("codec_name")
        frame_rate = video_stream.get("avg_frame_rate") or video_stream.get("r_frame_rate")
        meta["frame_rate"] = frame_rate
    elif audio_stream:
        meta["kind"] = "audio"
        meta["audio_codec"] = audio_stream.get("codec_name")
        sample_rate = audio_stream.get("sample_rate")
        meta["sample_rate"] = int(sample_rate) if str(sample_rate).isdigit() else None
        channels = audio_stream.get("channels")
        meta["channels"] = int(channels) if isinstance(channels, int) else channels
    else:
        return None

    return {k: v for k, v in meta.items() if v is not None}
