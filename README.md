# 🎬 Ultra Cool Discord Video Compressor
## Disclaimer: I wrote this entirely using claudecode. 

A blazing-fast Python utility to compress videos for Discord sharing (25MB limit). Featuring GPU acceleration, multiple quality outputs, batch processing, and more!

## ✨ Features

- **🎯 Discord Optimized**: Automatically targets Discord's 25MB file size limit
- **🚀 GPU Acceleration**: NVENC (NVIDIA), VAAPI (Intel/AMD), VideoToolbox (macOS) support
- **📊 Multiple Quality Outputs**: Generate multiple quality versions in one command
- **🎛️ 5 Quality Presets**: From "insane" quality to "potato" compression
- **📚 Batch Processing**: Process multiple videos simultaneously
- **📏 Smart Scaling**: Automatically scales down to 1280x720 max resolution
- **🎨 Beautiful UI**: Rich progress bars and detailed compression results
- **🌐 Cross-Platform**: Works on Windows, macOS, and Linux
- **⚡ Fast Processing**: Optimized encoding settings for speed
- **⏱️ Performance Tracking**: Real-time timing for individual files and batch operations
- **🏁 Benchmark Mode**: Compare CPU vs GPU performance across different quality settings

## 🔧 Requirements

- **Python 3.6+**
- **FFmpeg** (must be installed and in PATH)
- **Optional**: `rich` and `pyfiglet` for enhanced UI (`pip install rich pyfiglet`)

## 📦 Installation

1. **Install FFmpeg**:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `winget install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo dnf install ffmpeg` (Fedora)

2. **Clone/Download the script**:
   ```bash
   git clone <repository-url>
   cd video-cleaner

   # Optional: Install for enhanced UI
   pip install rich pyfiglet
   ```

## 🎮 Usage

### Basic Usage
```bash
# Simple compression
python video_compressor.py input_video.mp4 output_compressed.mp4

# Auto-generate output name
python video_compressor.py input_video.mp4

# With GPU acceleration
python video_compressor.py input_video.mp4 --gpu
```

### Multiple Quality Outputs
```bash
# Generate 3 different quality versions
python video_compressor.py input.mp4 --quality high,medium,low

# Generate ALL quality versions (5 files)
python video_compressor.py input.mp4 --quality all

# Multiple qualities with GPU acceleration
python video_compressor.py input.mp4 --quality all --gpu
```

### Batch Processing
```bash
# Process all MP4 files in directory
python video_compressor.py *.mp4 --batch

# Batch with custom output directory
python video_compressor.py *.mp4 --batch --output-dir compressed/

# Batch with multiple qualities and GPU
python video_compressor.py *.mp4 --batch --quality high,medium --gpu
```

### Interactive Mode
```bash
python video_compressor.py --interactive
```

### Benchmark Mode
```bash
# Test and compare CPU vs GPU performance
python video_compressor.py input.mp4 --benchmark

# Creates detailed performance comparison across 6 configurations:
# CPU/GPU × High/Medium/Low quality settings
```

## 🎛️ Quality Presets

| Quality | Emoji | CRF | Max Bitrate | Description | Best For |
|---------|-------|-----|-------------|-------------|----------|
| **insane** | 🔥 | 18 | 1200k | Maximum Quality | Professional work, archival |
| **high** | ✨ | 23 | 800k | High Quality | Important videos, presentations |
| **medium** | ⚡ | 28 | 500k | Balanced | Most Discord videos (default) |
| **low** | 🚀 | 32 | 300k | Speed Focus | Quick sharing, previews |
| **potato** | 🥔 | 35 | 200k | Tiny Size | When file size matters most |

## 🖥️ GPU Acceleration

The compressor automatically detects and uses hardware encoders:

- **NVIDIA GPUs**: H.264 NVENC (GTX 600+ series)
- **Intel/AMD GPUs** (Linux): VAAPI hardware encoding
- **macOS**: VideoToolbox hardware encoding
- **Automatic fallback**: Uses CPU if no GPU encoder available

GPU encoding is typically **3-10x faster** than CPU encoding!

## 📋 Command Line Options

```bash
python video_compressor.py [options] input_file(s) [output_file]

Options:
  --quality QUALITY     Quality preset or comma-separated list
                       (insane,high,medium,low,potato,all)
  --gpu                Enable GPU encoding (auto-detects hardware)
  --batch              Batch process multiple files
  --output-dir DIR     Output directory for batch processing
  --interactive        Launch interactive mode
  --benchmark          Run performance benchmark tests
  --no-banner          Skip the cool ASCII banner
  --help               Show help message
```

## 💡 Examples

### Single File Examples
```bash
# Basic compression
python video_compressor.py vacation.mp4

# High quality with GPU
python video_compressor.py movie.avi compressed.mp4 --quality high --gpu

# Generate all quality versions
python video_compressor.py presentation.mov --quality all

# Performance benchmark
python video_compressor.py test_video.mp4 --benchmark
```

### Batch Processing Examples
```bash
# Process all videos in current directory
python video_compressor.py *.mp4 *.avi *.mov --batch

# Multiple qualities for all files
python video_compressor.py *.mp4 --batch --quality high,medium,low --gpu

# Custom output directory
python video_compressor.py videos/*.mp4 --batch --output-dir discord_ready/
```

## 📊 Example Output

```
┌─ 🎉 Compression Results ─┐
│ Metric               Value            │
├──────────────────────────────────────│
│ 📂 Original Size    │ 87.3 MB         │
│ 📦 Compressed Size  │ 22.1 MB         │
│ 📉 Compression Ratio│ 74.7%           │
│ 💾 Space Saved     │ 65.2 MB         │
│ 🎯 Discord Ready   │ ✅ YES! Under 25MB│
└─────────────────────────────────────┘

🎉 Perfect! File is ready for Discord sharing!

┌─ ⚡ Performance ─┐
│ ⏱️ Compression time: 2m 34.5s │
│ 🖥️ Encoding: GPU               │
│ 📁 File: video.mp4            │
└───────────────────────────────┘
```

## 🏁 Benchmark Mode

The benchmark feature tests your system's performance across different encoding configurations:

### Benchmark Results Example:
```
┌─ 🏆 Benchmark Results for test.mp4 ─┐
│ Configuration │ Time     │ File Size │ Speed vs CPU │ Efficiency  │
├───────────────────────────────────────────────────────────────────│
│ CPU Medium    │ 2m 45.3s │ 22.1 MB   │ baseline     │ 0.13 MB/s   │
│ GPU Medium    │ 28.7s    │ 22.3 MB   │ 5.8x faster │ 0.78 MB/s   │
│ CPU High      │ 4m 12.1s │ 31.4 MB   │ 1.5x slower │ 0.12 MB/s   │
│ GPU High      │ 43.2s    │ 31.6 MB   │ 3.8x faster │ 0.73 MB/s   │
│ CPU Low       │ 1m 52.4s │ 15.7 MB   │ 1.5x faster │ 0.14 MB/s   │
│ GPU Low       │ 19.8s    │ 15.9 MB   │ 8.3x faster │ 0.80 MB/s   │
└───────────────────────────────────────────────────────────────────┘

┌─ 📊 Performance Analysis ─┐
│ 💡 Analysis:                │
│ • Fastest GPU: GPU Low (19.8s)     │
│ • Fastest CPU: CPU Low (1m 52.4s)  │
│ • GPU Speedup: 5.7x faster than CPU │
│ • Best quality/time ratio: GPU High │
└─────────────────────────────────────┘
```

### Benchmark Features:
- **🔄 6 Test Configurations**: CPU/GPU × High/Medium/Low quality
- **⏱️ Precise Timing**: Accurate performance measurements
- **📊 Speed Comparison**: Shows relative performance vs baseline
- **⚡ Efficiency Rating**: MB processed per second
- **🎯 Smart Analysis**: Recommends optimal settings
- **📁 Test Files**: Creates sample outputs in `benchmark_results/` folder

## 🔧 How It Works

The compressor applies Discord-specific optimizations:

1. **Video Codec**: H.264 with optimized settings (or GPU equivalent)
2. **Resolution**: Scales down to max 1280x720 if needed
3. **Bitrate Control**: Limits bitrate to prevent oversized files
4. **Audio**: AAC at 128k for optimal quality/size balance
5. **Format**: MP4 with web optimization flags (`faststart`)
6. **Smart Encoding**: Adjusts settings based on content and target size

## 🚨 Troubleshooting

### FFmpeg Issues
**"FFmpeg not found" error**:
- Install FFmpeg and ensure it's in your system PATH
- Test with: `ffmpeg -version`

### GPU Encoding Issues
**"GPU encoding requested but no supported GPU encoder found"**:
- Update your GPU drivers
- For NVIDIA: Ensure GTX 600 series or newer
- Windows: Download FFmpeg build with NVENC support

### File Size Issues
**File still too large for Discord**:
- Try `--quality low` or `--quality potato`
- Use `--quality all` to compare different sizes
- Consider trimming the video length first

### Performance Issues
**Very slow compression**:
- Use `--gpu` flag for hardware acceleration
- Lower quality settings (low/potato) are faster
- Large 4K videos will take longer to process

## ⏱️ Performance Tracking

All compression operations include detailed timing information:

### Individual File Timing:
- **⏱️ Compression time**: Precise timing for each file
- **🖥️ Encoder type**: Shows GPU or CPU encoding
- **📁 File identification**: Clear file naming in results

### Batch Operation Metrics:
- **📊 Total processing time**: Complete batch duration
- **📈 Average per file**: Mean processing time
- **🎯 Success rate**: Percentage of successful compressions
- **⚡ Throughput**: Files processed per minute

### Performance Benefits:
- **Compare GPU vs CPU**: See actual speed differences
- **Optimize workflow**: Identify bottlenecks and optimal settings
- **Track improvements**: Monitor performance over time
- **Quality analysis**: Balance speed vs quality for your needs

## 🎨 Interactive Features

- **📊 File size calculator**: Estimates compressed sizes for each quality
- **🎮 Interactive menu**: Easy-to-use interface for beginners
- **📋 Quality comparison**: See all quality options and their trade-offs
- **🔍 Video analysis**: Detailed information about your input files
- **🏁 Performance testing**: Built-in benchmark mode

## 📝 Output Files

When using multiple qualities, files are named with quality suffixes:
- `video_insane.mp4` - Maximum quality
- `video_high.mp4` - High quality
- `video_medium.mp4` - Balanced quality
- `video_low.mp4` - Speed focus
- `video_potato.mp4` - Minimum size

All output files default to `.mp4` format for maximum Discord compatibility.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the compressor!

## 📄 License

This project is open source and available under the MIT License.