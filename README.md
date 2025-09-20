# Discord Video Compressor

A Python utility to compress videos for Discord sharing, automatically optimizing file size to stay under the 25MB limit while maintaining good quality.

## Features

- **Discord Optimized**: Targets Discord's 25MB file size limit
- **Quality Control**: Three quality presets (high/medium/low)
- **Smart Scaling**: Automatically scales down large videos to 1280x720 max
- **Progress Feedback**: Shows compression statistics and file size analysis
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.6+
- FFmpeg (must be installed and in PATH)

## Installation

1. **Install FFmpeg**:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `winget install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo dnf install ffmpeg` (Fedora)

2. **Download the script**:
   ```bash
   # The script is ready to use - no additional Python packages needed!
   python video_compressor.py --help
   ```

## Usage

### Basic Usage
```bash
python video_compressor.py input_video.mp4 output_compressed.mp4
```

### Quality Settings
```bash
# High quality (larger file, better quality)
python video_compressor.py input.mp4 output.mp4 --quality high

# Medium quality (default, balanced)
python video_compressor.py input.mp4 output.mp4 --quality medium

# Low quality (smallest file)
python video_compressor.py input.mp4 output.mp4 --quality low
```

## Quality Presets

| Quality | CRF | Max Bitrate | Use Case |
|---------|-----|-------------|----------|
| High    | 23  | 800k        | Important content, quality matters |
| Medium  | 28  | 500k        | General use, balanced size/quality |
| Low     | 32  | 300k        | Maximum compression needed |

## Example Output

```
Input video: 1920x1080, 45.2s
Scaling video to fit 1280:720
Compressing: large_video.mp4 -> discord_ready.mp4
Quality: medium (CRF 28, max bitrate 500k)

✅ Compression completed!
Original size: 87.3 MB
Compressed size: 22.1 MB
Compression: 74.7% smaller
🎉 Perfect! File is under Discord's 25MB limit
```

## How It Works

The compressor applies Discord-specific optimizations:

1. **Video Codec**: H.264 with optimized settings
2. **Resolution**: Scales down to max 1280x720 if needed
3. **Bitrate**: Limits bitrate to prevent oversized files
4. **Audio**: AAC at 128k for good quality/size balance
5. **Format**: MP4 with web optimization flags

## Troubleshooting

**"FFmpeg not found" error**:
- Install FFmpeg and ensure it's in your system PATH
- Test with: `ffmpeg -version`

**File still too large**:
- Try `--quality low` setting
- Consider trimming the video length first

**Very slow compression**:
- Medium/Low quality settings are faster than High
- Large 4K videos will take longer to process