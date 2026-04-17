"""
批量压缩 asset/videos/ 下的原始大视频,输出到同目录下的 *_compressed.mp4。
目标:每个文件 < 100MB,便于推送至 GitHub。

依赖:系统已安装 ffmpeg,并且 ffmpeg 在 PATH 中。
用法:python compress_videos.py
"""

import subprocess
import sys
from pathlib import Path

VIDEO_DIR = Path(__file__).parent / "asset" / "videos"

# 要压缩的原始大视频
TARGETS = ["Park.mp4", "road.mp4", "resident.mp4", "waterfront.mp4"]

# H.264 CRF 质量参数:数值越大压缩越狠(范围 0-51,推荐 23-30)
# 28 通常能把 1080p 视频压到原大小的 5%-10%,视觉几乎无损
CRF = 28

# 最大宽度(高度按比例)。原片若是 4K,降到 1280 宽能极大减小体积
MAX_WIDTH = 1280

# 音频码率
AUDIO_BITRATE = "96k"


def compress(src: Path, dst: Path) -> bool:
    cmd = [
        "ffmpeg",
        "-y",                          # 覆盖已存在的输出文件
        "-i", str(src),
        "-vf", f"scale='min({MAX_WIDTH},iw)':-2",  # 宽度上限,高度自动(偶数)
        "-c:v", "libx264",
        "-preset", "slow",             # 慢=压得更小;可改 medium/fast
        "-crf", str(CRF),
        "-c:a", "aac",
        "-b:a", AUDIO_BITRATE,
        "-movflags", "+faststart",     # 网页播放优化(可秒开)
        str(dst),
    ]
    print(f"\n[压缩] {src.name}  ->  {dst.name}")
    result = subprocess.run(cmd)
    return result.returncode == 0


def human_size(n_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} TB"


def main() -> int:
    if not VIDEO_DIR.exists():
        print(f"找不到视频目录:{VIDEO_DIR}")
        return 1

    for name in TARGETS:
        src = VIDEO_DIR / name
        if not src.exists():
            print(f"[跳过] 不存在:{src}")
            continue

        dst = src.with_name(src.stem + "_compressed.mp4")
        ok = compress(src, dst)

        if ok and dst.exists():
            before = src.stat().st_size
            after = dst.stat().st_size
            ratio = after / before * 100
            print(f"  完成:{human_size(before)} -> {human_size(after)}  ({ratio:.1f}%)")
        else:
            print(f"  失败:{src.name}")
            return 1

    print("\n全部完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
