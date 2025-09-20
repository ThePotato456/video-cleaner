#!/usr/bin/env python3
"""
🎬 ULTRA COOL Discord Video Compressor 🎬
A blazing-fast Python utility to compress videos for Discord sharing (25MB limit)
Featuring: Progress bars, batch processing, ASCII art, and more!
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.align import Align
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None
    rprint = print

try:
    import pyfiglet
    FIGLET_AVAILABLE = True
except ImportError:
    FIGLET_AVAILABLE = False


class VideoCompressor:
    def __init__(self):
        self.discord_max_size_mb = 25
        self.discord_max_size_bytes = self.discord_max_size_mb * 1024 * 1024
        self.target_bitrate = "500k"
        self.max_resolution = "1280:720"
        self.console = Console() if RICH_AVAILABLE else None

        # Cool ASCII art and colors
        self.colors = {
            'primary': '#00ff88',
            'secondary': '#ff6b6b',
            'accent': '#4ecdc4',
            'warning': '#ffe66d',
            'error': '#ff6b6b',
            'success': '#00ff88'
        }

    def show_banner(self):
        """Display cool ASCII art banner"""
        if FIGLET_AVAILABLE:
            banner = pyfiglet.figlet_format("Video Compressor", font="slant")
            if RICH_AVAILABLE:
                banner_text = Text(banner, style=self.colors['primary'])
                self.console.print(Align.center(banner_text))
                self.console.print(Align.center("🎬 Ultra Cool Discord Video Compressor 🎬", style="bold cyan"))
                self.console.print(Align.center("Compress videos like a pro!", style="italic"))
            else:
                print(banner)
                print("🎬 Ultra Cool Discord Video Compressor 🎬")
        else:
            welcome = "="*60 + "\n" + "🎬 ULTRA COOL DISCORD VIDEO COMPRESSOR 🎬\n" + "="*60
            if RICH_AVAILABLE:
                self.console.print(welcome, style="bold cyan")
            else:
                print(welcome)

    def check_ffmpeg(self):
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(['ffmpeg', '-version'],
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _get_gpu_encoder(self):
        """Detect and return the best available GPU encoder"""
        import platform
        system = platform.system().lower()

        if system == 'windows':
            encoders_to_test = ['h264_nvenc']  # Only NVENC on Windows
        elif system == 'darwin':
            encoders_to_test = ['h264_videotoolbox']  # Only VideoToolbox on macOS
        else:
            encoders_to_test = ['h264_nvenc', 'h264_vaapi']  # Both on Linux

        if RICH_AVAILABLE:
            self.console.print("🔍 Checking for GPU encoders...", style="cyan")
        else:
            print("🔍 Checking for GPU encoders...")

        # First try to check if encoders exist in FFmpeg
        try:
            result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                available_encoders = result.stdout.lower()
                for encoder in encoders_to_test:
                    if encoder in available_encoders:
                        if RICH_AVAILABLE:
                            self.console.print(f"✅ Found {encoder} in FFmpeg", style="green")
                        else:
                            print(f"✅ Found {encoder} in FFmpeg")

                        # Found encoder in list, now test if it actually works
                        if self._test_gpu_encoder(encoder):
                            if RICH_AVAILABLE:
                                self.console.print(f"🚀 {encoder} test successful!", style="bold green")
                            else:
                                print(f"🚀 {encoder} test successful!")
                            return encoder
                        else:
                            if RICH_AVAILABLE:
                                self.console.print(f"❌ {encoder} test failed", style="red")
                            else:
                                print(f"❌ {encoder} test failed")
                    else:
                        if RICH_AVAILABLE:
                            self.console.print(f"⚠️ {encoder} not found in FFmpeg", style="yellow")
                        else:
                            print(f"⚠️ {encoder} not found in FFmpeg")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            if RICH_AVAILABLE:
                self.console.print(f"❌ Error checking encoders: {e}", style="red")
            else:
                print(f"❌ Error checking encoders: {e}")

        return None

    def _test_gpu_encoder(self, encoder):
        """Test if a specific GPU encoder actually works"""
        if RICH_AVAILABLE:
            self.console.print(f"🧪 Testing {encoder}...", style="cyan")
        else:
            print(f"🧪 Testing {encoder}...")

        try:
            # Use minimum size that works with all GPU encoders (NVENC needs at least 256x256)
            test_size = '256x256'

            result = subprocess.run([
                'ffmpeg', '-hide_banner', '-loglevel', 'error',
                '-f', 'lavfi', '-i', f'testsrc=duration=0.1:size={test_size}:rate=1',
                '-c:v', encoder, '-frames:v', '1', '-f', 'null', '-'
            ], capture_output=True, timeout=15)

            if RICH_AVAILABLE:
                self.console.print(f"📊 Test result: return code {result.returncode}", style="blue")
                if result.stderr:
                    self.console.print(f"📝 Error output: {result.stderr.decode()[:200]}", style="yellow")
            else:
                print(f"📊 Test result: return code {result.returncode}")
                if result.stderr:
                    print(f"📝 Error output: {result.stderr.decode()[:200]}")

            # Return True if command succeeded or if it's just a warning about no output
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            if RICH_AVAILABLE:
                self.console.print(f"❌ Test exception: {e}", style="red")
            else:
                print(f"❌ Test exception: {e}")
            return False

    def get_video_info(self, input_path):
        """Get detailed video information with cool display"""
        if RICH_AVAILABLE:
            with self.console.status("🔍 Analyzing video...", spinner="dots"):
                time.sleep(0.5)  # Dramatic pause
                info = self._extract_video_info(input_path)
        else:
            print("🔍 Analyzing video...")
            info = self._extract_video_info(input_path)

        if info and RICH_AVAILABLE:
            self._display_video_info(info, input_path)
        elif info:
            self._display_video_info_simple(info, input_path)

        return info

    def _extract_video_info(self, input_path):
        """Extract video information using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(input_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                data = json.loads(result.stdout)

                # Find video stream
                video_stream = None
                audio_stream = None
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'video' and not video_stream:
                        video_stream = stream
                    elif stream.get('codec_type') == 'audio' and not audio_stream:
                        audio_stream = stream

                if video_stream:
                    width = int(video_stream.get('width', 0))
                    height = int(video_stream.get('height', 0))
                    duration = float(data.get('format', {}).get('duration', 0))
                    bitrate = int(data.get('format', {}).get('bit_rate', 0)) // 1000
                    codec = video_stream.get('codec_name', 'unknown')
                    fps = eval(video_stream.get('r_frame_rate', '0/1'))

                    return {
                        'width': width,
                        'height': height,
                        'duration': duration,
                        'bitrate': bitrate,
                        'codec': codec,
                        'fps': fps,
                        'has_audio': audio_stream is not None,
                        'format': data.get('format', {})
                    }

        except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError, ZeroDivisionError):
            pass

        return None

    def _display_video_info(self, info, input_path):
        """Display video info in a cool table format"""
        table = Table(title="📹 Video Information", show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan", width=15)
        table.add_column("Value", style="green")

        file_size = Path(input_path).stat().st_size / (1024 * 1024)

        table.add_row("📁 Filename", Path(input_path).name)
        table.add_row("📏 Resolution", f"{info['width']}x{info['height']}")
        table.add_row("⏱️ Duration", f"{info['duration']:.1f}s ({info['duration']//60:.0f}m {info['duration']%60:.0f}s)")
        table.add_row("🎯 Codec", info['codec'].upper())
        table.add_row("🚀 FPS", f"{info['fps']:.1f}")
        table.add_row("🔊 Audio", "✅ Yes" if info['has_audio'] else "❌ No")
        table.add_row("💾 File Size", f"{file_size:.1f} MB")
        if info['bitrate'] > 0:
            table.add_row("⚡ Bitrate", f"{info['bitrate']} kbps")

        self.console.print(table)

    def _display_video_info_simple(self, info, input_path):
        """Simple video info display for when rich is not available"""
        file_size = Path(input_path).stat().st_size / (1024 * 1024)
        print(f"\n📹 Video Information:")
        print(f"📁 Filename: {Path(input_path).name}")
        print(f"📏 Resolution: {info['width']}x{info['height']}")
        print(f"⏱️ Duration: {info['duration']:.1f}s")
        print(f"🎯 Codec: {info['codec'].upper()}")
        print(f"💾 File Size: {file_size:.1f} MB")

    def calculate_scale_filter(self, width, height):
        """Calculate optimal scaling to fit Discord requirements"""
        max_width, max_height = 1280, 720

        if width <= max_width and height <= max_height:
            return None  # No scaling needed

        # Calculate scale to fit within bounds while maintaining aspect ratio
        scale_filter = f"scale='min({max_width},iw)':'min({max_height},ih)':force_original_aspect_ratio=decrease"
        return scale_filter

    def compress_video(self, input_path, output_path, quality="medium", use_gpu=False):
        """Compress video with cool progress tracking and Discord optimization"""
        import time
        start_time = time.time()

        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Get video info with cool display
        video_info = self.get_video_info(input_path)

        # Enhanced quality presets with emoji descriptions
        quality_settings = {
            "insane": {"crf": "18", "preset": "veryslow", "maxrate": "1200k", "bufsize": "2400k", "emoji": "🔥", "desc": "Maximum Quality"},
            "high": {"crf": "23", "preset": "slow", "maxrate": "800k", "bufsize": "1600k", "emoji": "✨", "desc": "High Quality"},
            "medium": {"crf": "28", "preset": "fast", "maxrate": "500k", "bufsize": "1000k", "emoji": "⚡", "desc": "Balanced"},
            "low": {"crf": "32", "preset": "fast", "maxrate": "300k", "bufsize": "600k", "emoji": "🚀", "desc": "Speed Focus"},
            "potato": {"crf": "35", "preset": "veryfast", "maxrate": "200k", "bufsize": "400k", "emoji": "🥔", "desc": "Tiny Size"}
        }

        settings = quality_settings.get(quality, quality_settings["medium"])

        # Display compression settings
        if RICH_AVAILABLE:
            panel = Panel(f"{settings['emoji']} {settings['desc']} (CRF {settings['crf']}, {settings['maxrate']} max bitrate)",
                         title="🎯 Compression Settings", border_style="cyan")
            self.console.print(panel)
        else:
            print(f"\n🎯 Using {quality} quality: {settings['desc']} (CRF {settings['crf']})")

        # Build FFmpeg command with GPU support
        cmd = ['ffmpeg', '-i', str(input_path)]

        if use_gpu:
            # Try to detect and use appropriate GPU encoder
            gpu_encoder = self._get_gpu_encoder()
            if gpu_encoder:
                cmd.extend(['-c:v', gpu_encoder])
                # GPU encoders use different quality settings
                if 'nvenc' in gpu_encoder:
                    cmd.extend(['-preset', 'p4', '-cq', settings['crf']])
                elif 'vaapi' in gpu_encoder:
                    cmd.extend(['-qp', settings['crf']])
                elif 'videotoolbox' in gpu_encoder:
                    cmd.extend(['-q:v', str(int(int(settings['crf']) * 0.8))])

                cmd.extend(['-maxrate', settings['maxrate'], '-bufsize', settings['bufsize']])

                if RICH_AVAILABLE:
                    self.console.print(f"🚀 Using GPU encoder: {gpu_encoder}", style="green")
                else:
                    print(f"🚀 Using GPU encoder: {gpu_encoder}")
            else:
                if RICH_AVAILABLE:
                    self.console.print("⚠️ GPU encoding requested but no supported GPU encoder found, falling back to CPU", style="yellow")
                else:
                    print("⚠️ GPU encoding requested but no supported GPU encoder found, falling back to CPU")
                use_gpu = False

        if not use_gpu:
            # Fallback to CPU encoding
            cmd.extend([
                '-c:v', 'libx264',
                '-preset', settings['preset'],
                '-crf', settings['crf'],
                '-maxrate', settings['maxrate'],
                '-bufsize', settings['bufsize']
            ])

        # Add scaling if needed
        if video_info:
            scale_filter = self.calculate_scale_filter(video_info['width'], video_info['height'])
            if scale_filter:
                cmd.extend(['-vf', scale_filter])
                if RICH_AVAILABLE:
                    self.console.print(f"📏 Scaling video to fit {self.max_resolution}", style="yellow")
                else:
                    print(f"📏 Scaling video to fit {self.max_resolution}")

        # Audio settings
        cmd.extend([
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            '-y',
            str(output_path)
        ])

        try:
            result = self._run_compression_with_progress(cmd, input_path, output_path, video_info)

            # Calculate elapsed time
            end_time = time.time()
            elapsed_time = end_time - start_time

            # If successful, show timing and return result
            if result:
                self._display_timing_info(elapsed_time, input_path, use_gpu)

            return result
        except subprocess.TimeoutExpired:
            if RICH_AVAILABLE:
                self.console.print("⏰ Error: Compression timed out (30 minutes)", style="bold red")
            else:
                print("⏰ Error: Compression timed out (30 minutes)")
            return False

    def _display_timing_info(self, elapsed_time, input_path, use_gpu):
        """Display compression timing information"""
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60

        encoding_type = "GPU" if use_gpu else "CPU"
        time_str = f"{minutes}m {seconds:.1f}s" if minutes > 0 else f"{seconds:.1f}s"

        if RICH_AVAILABLE:
            timing_panel = Panel(
                f"⏱️ Compression time: {time_str}\n"
                f"🖥️ Encoding: {encoding_type}\n"
                f"📁 File: {input_path.name}",
                title="⚡ Performance",
                border_style="green"
            )
            self.console.print(timing_panel)
        else:
            print(f"\n⚡ Performance:")
            print(f"⏱️ Compression time: {time_str}")
            print(f"🖥️ Encoding: {encoding_type}")
            print(f"📁 File: {input_path.name}")

    def _run_compression_with_progress(self, cmd, input_path, output_path, video_info):
        """Run compression with real-time progress tracking"""
        duration = video_info['duration'] if video_info else 0

        if RICH_AVAILABLE and duration > 0:
            return self._run_with_rich_progress(cmd, input_path, output_path, duration)
        else:
            return self._run_simple_compression(cmd, input_path, output_path)

    def _run_with_rich_progress(self, cmd, input_path, output_path, duration):
        """Run compression with rich progress bar"""
        # Add progress reporting to FFmpeg command
        progress_cmd = cmd + ['-progress', 'pipe:2']  # Send progress to stderr

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:

            task = progress.add_task(f"🎬 Compressing {input_path.name}...", total=duration)

            process = subprocess.Popen(progress_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     universal_newlines=True, bufsize=1)

            current_time = 0
            error_output = []

            # Read both stdout and stderr
            import select
            import sys

            # For Windows compatibility, use a simpler approach
            if sys.platform == 'win32':
                return self._run_windows_progress(process, task, progress, duration, input_path, output_path)

            # Unix-like systems can use select
            while True:
                if process.poll() is not None:
                    break

                # Read stderr for progress info
                stderr_line = process.stderr.readline()
                if stderr_line:
                    error_output.append(stderr_line)
                    # Parse FFmpeg progress from stderr
                    if 'out_time_us=' in stderr_line:
                        time_match = re.search(r'out_time_us=(\d+)', stderr_line)
                        if time_match:
                            current_time = int(time_match.group(1)) / 1000000  # Convert microseconds to seconds
                            progress.update(task, completed=min(current_time, duration))
                    elif 'out_time=' in stderr_line:
                        time_match = re.search(r'out_time=(\d+\.\d+)', stderr_line)
                        if time_match:
                            current_time = float(time_match.group(1))
                            progress.update(task, completed=min(current_time, duration))

            process.wait()

            if process.returncode == 0:
                progress.update(task, completed=duration, description=f"✅ {input_path.name} compressed!")
                time.sleep(0.5)  # Show completion briefly
                return self.analyze_result(input_path, output_path)
            else:
                full_error = ''.join(error_output)
                self.console.print(f"❌ FFmpeg error: {full_error[-500:]}", style="bold red")  # Show last 500 chars
                return False

    def _run_windows_progress(self, process, task, progress, duration, input_path, output_path):
        """Windows-specific progress handling"""
        import threading
        import queue

        error_output = []
        current_time = 0

        def read_stderr():
            while True:
                line = process.stderr.readline()
                if not line:
                    break
                error_output.append(line)

                # Parse progress
                if 'out_time_us=' in line:
                    time_match = re.search(r'out_time_us=(\d+)', line)
                    if time_match:
                        nonlocal current_time
                        current_time = int(time_match.group(1)) / 1000000
                        progress.update(task, completed=min(current_time, duration))
                elif 'out_time=' in line:
                    time_match = re.search(r'out_time=(\d+\.\d+)', line)
                    if time_match:
                        current_time = float(time_match.group(1))
                        progress.update(task, completed=min(current_time, duration))

        # Start stderr reading thread
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stderr_thread.start()

        # Wait for process to complete
        process.wait()
        stderr_thread.join(timeout=1.0)  # Give thread a moment to finish

        if process.returncode == 0:
            progress.update(task, completed=duration, description=f"✅ {input_path.name} compressed!")
            time.sleep(0.5)
            return self.analyze_result(input_path, output_path)
        else:
            full_error = ''.join(error_output)
            self.console.print(f"❌ FFmpeg error: {full_error[-500:]}", style="bold red")
            return False

    def _run_simple_compression(self, cmd, input_path, output_path):
        """Simple compression without rich progress"""
        print(f"🎬 Compressing: {input_path.name} -> {output_path.name}")
        print("⏳ This may take a while...")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

        if result.returncode == 0:
            return self.analyze_result(input_path, output_path)
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False

    def analyze_result(self, input_path, output_path):
        """Analyze compression results with cool visual feedback"""
        if not output_path.exists():
            if RICH_AVAILABLE:
                self.console.print("❌ Error: Output file was not created", style="bold red")
            else:
                print("❌ Error: Output file was not created")
            return False

        input_size = input_path.stat().st_size
        output_size = output_path.stat().st_size

        input_mb = input_size / (1024 * 1024)
        output_mb = output_size / (1024 * 1024)
        compression_ratio = (1 - output_size / input_size) * 100
        space_saved = input_mb - output_mb

        if RICH_AVAILABLE:
            # Create awesome results table
            results_table = Table(title="🎉 Compression Results", show_header=True, header_style="bold green")
            results_table.add_column("Metric", style="cyan", width=20)
            results_table.add_column("Value", style="green")

            results_table.add_row("📂 Original Size", f"{input_mb:.1f} MB")
            results_table.add_row("📦 Compressed Size", f"{output_mb:.1f} MB")
            results_table.add_row("📉 Compression Ratio", f"{compression_ratio:.1f}%")
            results_table.add_row("💾 Space Saved", f"{space_saved:.1f} MB")

            # Discord compatibility check
            if output_size <= self.discord_max_size_bytes:
                results_table.add_row("🎯 Discord Ready", "✅ YES! Under 25MB limit")
                discord_style = "bold green"
                discord_msg = f"🎉 Perfect! File is ready for Discord sharing!"
            else:
                over_limit = output_mb - self.discord_max_size_mb
                results_table.add_row("🎯 Discord Ready", f"⚠️ NO - {over_limit:.1f}MB over limit")
                discord_style = "bold yellow"
                discord_msg = f"⚠️ File is still {over_limit:.1f}MB over Discord's 25MB limit\n💡 Try 'low' or 'potato' quality for smaller size"

            self.console.print(results_table)
            self.console.print(Panel(discord_msg, border_style=discord_style))

        else:
            print(f"\n🎉 Compression completed!")
            print(f"📂 Original size: {input_mb:.1f} MB")
            print(f"📦 Compressed size: {output_mb:.1f} MB")
            print(f"📉 Compression: {compression_ratio:.1f}% smaller")
            print(f"💾 Space saved: {space_saved:.1f} MB")

            if output_size <= self.discord_max_size_bytes:
                print(f"🎉 Perfect! File is under Discord's {self.discord_max_size_mb}MB limit")
            else:
                print(f"⚠️ Warning: File is still {output_mb - self.discord_max_size_mb:.1f}MB over Discord's limit")
                print("💡 Try using 'low' or 'potato' quality setting for smaller file size")

        return True

    def compress_video_multiple_qualities(self, input_path, qualities: List[str], use_gpu=False):
        """Compress a single video with multiple quality settings"""
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        successful = []
        failed = []

        for quality in qualities:
            # Validate quality
            valid_qualities = ['insane', 'high', 'medium', 'low', 'potato']
            if quality not in valid_qualities:
                if RICH_AVAILABLE:
                    self.console.print(f"⚠️ Invalid quality '{quality}', skipping...", style="yellow")
                else:
                    print(f"⚠️ Invalid quality '{quality}', skipping...")
                failed.append((quality, "Invalid quality setting"))
                continue

            # Generate output filename with quality suffix, default to .mp4
            output_path = input_path.with_stem(f"{input_path.stem}_{quality}").with_suffix('.mp4')

            if RICH_AVAILABLE:
                self.console.print(f"\n🎯 Processing with {quality} quality...", style="bold blue")
            else:
                print(f"\n🎯 Processing with {quality} quality...")

            try:
                success = self.compress_video(input_path, output_path, quality, use_gpu)
                if success:
                    successful.append(str(output_path))
                else:
                    failed.append((quality, "Compression failed"))
            except Exception as e:
                failed.append((quality, str(e)))

        return successful, failed

    def run_benchmark(self, input_path):
        """Run comprehensive benchmark tests on a video file"""
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        import time

        if RICH_AVAILABLE:
            self.console.print("🏁 Starting benchmark tests...", style="bold cyan")
            self.console.print("This will test various encoding configurations to find optimal settings.", style="cyan")
        else:
            print("🏁 Starting benchmark tests...")
            print("This will test various encoding configurations to find optimal settings.")

        # Create benchmark directory
        benchmark_dir = Path("benchmark_results")
        benchmark_dir.mkdir(exist_ok=True)

        benchmark_results = []

        # Test configurations: (quality, use_gpu, description)
        test_configs = [
            ("medium", False, "CPU Medium"),
            ("medium", True, "GPU Medium"),
            ("high", False, "CPU High"),
            ("high", True, "GPU High"),
            ("low", False, "CPU Low"),
            ("low", True, "GPU Low"),
        ]

        total_tests = len(test_configs)

        for i, (quality, use_gpu, description) in enumerate(test_configs, 1):
            if RICH_AVAILABLE:
                self.console.print(f"\n🧪 Test {i}/{total_tests}: {description}", style="bold blue")
            else:
                print(f"\n🧪 Test {i}/{total_tests}: {description}")

            # Generate output filename
            output_filename = f"benchmark_{quality}_{('gpu' if use_gpu else 'cpu')}.mp4"
            output_path = benchmark_dir / output_filename

            try:
                start_time = time.time()
                success = self.compress_video(input_path, output_path, quality, use_gpu)
                end_time = time.time()

                if success and output_path.exists():
                    elapsed_time = end_time - start_time
                    output_size = output_path.stat().st_size / (1024 * 1024)  # MB

                    benchmark_results.append({
                        'description': description,
                        'quality': quality,
                        'gpu': use_gpu,
                        'time': elapsed_time,
                        'size_mb': output_size,
                        'output_path': output_path,
                        'success': True
                    })

                    if RICH_AVAILABLE:
                        minutes = int(elapsed_time // 60)
                        seconds = elapsed_time % 60
                        time_str = f"{minutes}m {seconds:.1f}s" if minutes > 0 else f"{seconds:.1f}s"
                        self.console.print(f"✅ Completed in {time_str} - {output_size:.1f}MB", style="green")
                    else:
                        print(f"✅ Completed in {elapsed_time:.1f}s - {output_size:.1f}MB")
                else:
                    benchmark_results.append({
                        'description': description,
                        'quality': quality,
                        'gpu': use_gpu,
                        'success': False
                    })
                    if RICH_AVAILABLE:
                        self.console.print("❌ Failed", style="red")
                    else:
                        print("❌ Failed")

            except Exception as e:
                benchmark_results.append({
                    'description': description,
                    'quality': quality,
                    'gpu': use_gpu,
                    'success': False,
                    'error': str(e)
                })
                if RICH_AVAILABLE:
                    self.console.print(f"❌ Error: {e}", style="red")
                else:
                    print(f"❌ Error: {e}")

        # Display benchmark results
        self._display_benchmark_results(benchmark_results, input_path)

        return benchmark_results

    def _display_benchmark_results(self, results, input_path):
        """Display comprehensive benchmark results"""
        successful_results = [r for r in results if r.get('success', False)]

        if not successful_results:
            if RICH_AVAILABLE:
                self.console.print("❌ No successful benchmark tests completed", style="bold red")
            else:
                print("❌ No successful benchmark tests completed")
            return

        if RICH_AVAILABLE:
            # Create benchmark results table
            table = Table(title=f"🏆 Benchmark Results for {input_path.name}", show_header=True, header_style="bold magenta")
            table.add_column("Configuration", style="cyan", width=15)
            table.add_column("Time", style="green", width=10)
            table.add_column("File Size", style="yellow", width=10)
            table.add_column("Speed vs CPU", style="blue", width=12)
            table.add_column("Efficiency", style="purple", width=12)

            # Find CPU medium baseline for comparison
            cpu_medium_time = None
            for result in successful_results:
                if result['quality'] == 'medium' and not result['gpu']:
                    cpu_medium_time = result['time']
                    break

            # Add results to table
            for result in successful_results:
                # Format time
                time = result['time']
                minutes = int(time // 60)
                time_str = f"{minutes}m {time % 60:.1f}s" if minutes > 0 else f"{time:.1f}s"

                # Calculate speed comparison
                if cpu_medium_time and cpu_medium_time > 0:
                    speed_multiplier = cpu_medium_time / time
                    if speed_multiplier > 1:
                        speed_str = f"{speed_multiplier:.1f}x faster"
                    else:
                        speed_str = f"{1/speed_multiplier:.1f}x slower"
                else:
                    speed_str = "baseline"

                # Calculate efficiency (MB per second)
                efficiency = result['size_mb'] / time
                efficiency_str = f"{efficiency:.2f} MB/s"

                table.add_row(
                    result['description'],
                    time_str,
                    f"{result['size_mb']:.1f} MB",
                    speed_str,
                    efficiency_str
                )

            self.console.print(table)

            # Performance analysis
            self._display_benchmark_analysis(successful_results)

        else:
            # Simple text output
            print(f"\n🏆 Benchmark Results for {input_path.name}")
            print("="*60)

            for result in successful_results:
                time = result['time']
                print(f"{result['description']:15} {time:6.1f}s  {result['size_mb']:6.1f}MB")

            # Simple analysis
            self._display_benchmark_analysis_simple(successful_results)

    def _display_benchmark_analysis(self, results):
        """Display detailed benchmark analysis with Rich formatting"""
        # Find best GPU and CPU results
        gpu_results = [r for r in results if r['gpu']]
        cpu_results = [r for r in results if not r['gpu']]

        if gpu_results and cpu_results:
            # Find fastest GPU and CPU
            fastest_gpu = min(gpu_results, key=lambda x: x['time'])
            fastest_cpu = min(cpu_results, key=lambda x: x['time'])

            gpu_speedup = fastest_cpu['time'] / fastest_gpu['time']

            analysis_text = f"""
💡 Analysis:
• Fastest GPU: {fastest_gpu['description']} ({fastest_gpu['time']:.1f}s)
• Fastest CPU: {fastest_cpu['description']} ({fastest_cpu['time']:.1f}s)
• GPU Speedup: {gpu_speedup:.1f}x faster than CPU
• Best quality/time ratio: {self._find_best_quality_time_ratio(results)}
            """.strip()

            analysis_panel = Panel(
                analysis_text,
                title="📊 Performance Analysis",
                border_style="cyan"
            )
            self.console.print(analysis_panel)

    def _display_benchmark_analysis_simple(self, results):
        """Display simple benchmark analysis"""
        gpu_results = [r for r in results if r['gpu']]
        cpu_results = [r for r in results if not r['gpu']]

        if gpu_results and cpu_results:
            fastest_gpu = min(gpu_results, key=lambda x: x['time'])
            fastest_cpu = min(cpu_results, key=lambda x: x['time'])
            gpu_speedup = fastest_cpu['time'] / fastest_gpu['time']

            print(f"\n📊 Analysis:")
            print(f"Fastest GPU: {fastest_gpu['description']} ({fastest_gpu['time']:.1f}s)")
            print(f"Fastest CPU: {fastest_cpu['description']} ({fastest_cpu['time']:.1f}s)")
            print(f"GPU Speedup: {gpu_speedup:.1f}x faster")

    def _find_best_quality_time_ratio(self, results):
        """Find the configuration with the best quality/time trade-off"""
        quality_scores = {'low': 1, 'medium': 2, 'high': 3}
        best_ratio = 0
        best_config = None

        for result in results:
            quality_score = quality_scores.get(result['quality'], 2)
            ratio = quality_score / result['time']  # Higher is better

            if ratio > best_ratio:
                best_ratio = ratio
                best_config = result

        return best_config['description'] if best_config else "Unknown"

    def compress_multiple_videos(self, input_paths: List[str], output_dir: str, quality: str = "medium", use_gpu=False):
        """Batch compress multiple videos with progress tracking"""
        import time
        batch_start_time = time.time()

        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        successful = []
        failed = []

        if RICH_AVAILABLE:
            self.console.print(f"🚀 Starting batch compression of {len(input_paths)} videos...", style="bold cyan")
        else:
            print(f"🚀 Starting batch compression of {len(input_paths)} videos...")

        for i, input_path in enumerate(input_paths, 1):
            input_path = Path(input_path)
            if not input_path.exists():
                failed.append((str(input_path), "File not found"))
                continue

            output_path = output_dir / f"{input_path.stem}_compressed{input_path.suffix}"

            if RICH_AVAILABLE:
                self.console.print(f"\n📹 Processing {i}/{len(input_paths)}: {input_path.name}", style="bold blue")
            else:
                print(f"\n📹 Processing {i}/{len(input_paths)}: {input_path.name}")

            try:
                success = self.compress_video(input_path, output_path, quality, use_gpu)
                if success:
                    successful.append(str(output_path))
                else:
                    failed.append((str(input_path), "Compression failed"))
            except Exception as e:
                failed.append((str(input_path), str(e)))

        # Calculate and display batch timing
        batch_end_time = time.time()
        batch_elapsed_time = batch_end_time - batch_start_time

        # Show batch results with timing
        self._show_batch_results(successful, failed, batch_elapsed_time, use_gpu)
        return len(successful), len(failed)

    def _show_batch_results(self, successful: List[str], failed: List[tuple], batch_elapsed_time=None, use_gpu=False):
        """Display batch processing results with timing"""
        if RICH_AVAILABLE:
            # Build results text with timing
            results_text = (
                f"✅ Successfully compressed: {len(successful)} videos\n" +
                f"❌ Failed: {len(failed)} videos\n" +
                f"🎯 Success rate: {len(successful)/(len(successful)+len(failed))*100:.1f}%"
            )

            # Add timing information if available
            if batch_elapsed_time:
                minutes = int(batch_elapsed_time // 60)
                seconds = batch_elapsed_time % 60
                time_str = f"{minutes}m {seconds:.1f}s" if minutes > 0 else f"{seconds:.1f}s"
                encoding_type = "GPU" if use_gpu else "CPU"

                # Calculate average time per file
                total_files = len(successful) + len(failed)
                if total_files > 0:
                    avg_time_per_file = batch_elapsed_time / total_files
                    avg_str = f"{avg_time_per_file:.1f}s" if avg_time_per_file < 60 else f"{int(avg_time_per_file // 60)}m {avg_time_per_file % 60:.1f}s"

                    results_text += (
                        f"\n⏱️ Total time: {time_str}\n" +
                        f"🖥️ Encoding: {encoding_type}\n" +
                        f"📈 Avg per file: {avg_str}"
                    )

            results_panel = Panel(
                results_text,
                title="📊 Batch Processing Results",
                border_style="green" if len(failed) == 0 else "yellow"
            )
            self.console.print(results_panel)

            if failed:
                error_table = Table(title="❌ Failed Files", show_header=True)
                error_table.add_column("File", style="red")
                error_table.add_column("Error", style="yellow")
                for file_path, error in failed:
                    error_table.add_row(Path(file_path).name, error)
                self.console.print(error_table)
        else:
            print(f"\n📊 Batch Processing Results:")
            print(f"✅ Successfully compressed: {len(successful)} videos")
            print(f"❌ Failed: {len(failed)} videos")

            # Add timing information if available
            if batch_elapsed_time:
                minutes = int(batch_elapsed_time // 60)
                seconds = batch_elapsed_time % 60
                time_str = f"{minutes}m {seconds:.1f}s" if minutes > 0 else f"{seconds:.1f}s"
                encoding_type = "GPU" if use_gpu else "CPU"

                print(f"⏱️ Total time: {time_str}")
                print(f"🖥️ Encoding: {encoding_type}")

                # Calculate average time per file
                total_files = len(successful) + len(failed)
                if total_files > 0:
                    avg_time_per_file = batch_elapsed_time / total_files
                    avg_str = f"{avg_time_per_file:.1f}s" if avg_time_per_file < 60 else f"{int(avg_time_per_file // 60)}m {avg_time_per_file % 60:.1f}s"
                    print(f"📈 Avg per file: {avg_str}")

            if failed:
                print(f"\n❌ Failed files:")
                for file_path, error in failed:
                    print(f"  - {Path(file_path).name}: {error}")


def main():
    parser = argparse.ArgumentParser(
        description="Ultra Cool Discord Video Compressor - Compress videos like a pro!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single file compression
  python video_compressor.py input.mp4 output.mp4
  python video_compressor.py input.mov output.mp4 --quality high
  python video_compressor.py large_video.avi compressed.mp4 --quality potato

  # Multiple quality outputs (generates multiple files)
  python video_compressor.py input.mp4 --quality high,medium,low
  python video_compressor.py input.mp4 --quality all
  python video_compressor.py input.mp4 output.mp4 --quality insane,potato

  # GPU encoding (faster with supported hardware)
  python video_compressor.py input.mp4 output.mp4 --gpu
  python video_compressor.py input.mp4 --quality all --gpu

  # Batch compression
  python video_compressor.py *.mp4 --batch --output-dir compressed/
  python video_compressor.py video1.mp4 video2.mov video3.avi --batch --output-dir ./compressed/
  python video_compressor.py *.mp4 --batch --quality all

  # Interactive mode
  python video_compressor.py --interactive

  # Benchmark mode (compare CPU vs GPU performance)
  python video_compressor.py input.mp4 --benchmark
        """
    )

    parser.add_argument('files', nargs='*', help='Input video file path(s) and optional output path')
    parser.add_argument('--quality', default='medium',
                       help='Compression quality - single value, comma-separated list, or "all" for every quality (e.g., "medium", "high,low", or "all")')
    parser.add_argument('--batch', action='store_true', help='Batch process multiple files')
    parser.add_argument('--output-dir', help='Output directory for batch processing')
    parser.add_argument('--interactive', action='store_true', help='Launch interactive mode')
    parser.add_argument('--no-banner', action='store_true', help='Skip the cool banner')
    parser.add_argument('--gpu', action='store_true', help='Enable GPU encoding (requires NVENC/VAAPI/VideoToolbox support)')
    parser.add_argument('--benchmark', action='store_true', help='Run benchmark tests comparing CPU vs GPU and different quality settings')

    args = parser.parse_args()

    compressor = VideoCompressor()

    # Show cool banner unless disabled
    if not args.no_banner:
        compressor.show_banner()
        print()  # Add some space

    # Check if FFmpeg is available
    if not compressor.check_ffmpeg():
        if RICH_AVAILABLE:
            compressor.console.print("❌ Error: FFmpeg not found!", style="bold red")
            compressor.console.print("Please install FFmpeg and make sure it's in your PATH", style="yellow")
            compressor.console.print("Download from: https://ffmpeg.org/download.html", style="cyan")
        else:
            print("❌ Error: FFmpeg not found!")
            print("Please install FFmpeg and make sure it's in your PATH")
            print("Download from: https://ffmpeg.org/download.html")
        return 1

    try:
        # Interactive mode
        if args.interactive:
            return run_interactive_mode(compressor)

        # Benchmark mode
        if args.benchmark:
            if len(args.files) != 1:
                if RICH_AVAILABLE:
                    compressor.console.print("❌ Benchmark mode requires exactly one input file", style="bold red")
                else:
                    print("❌ Benchmark mode requires exactly one input file")
                return 1

            try:
                compressor.run_benchmark(args.files[0])
                return 0
            except Exception as e:
                if RICH_AVAILABLE:
                    compressor.console.print(f"❌ Benchmark error: {e}", style="bold red")
                else:
                    print(f"❌ Benchmark error: {e}")
                return 1

        # Parse quality argument - check if comma-separated or "all"
        if args.quality.lower().strip() == 'all':
            qualities = ['insane', 'high', 'medium', 'low', 'potato']
        else:
            qualities = [q.strip() for q in args.quality.split(',') if q.strip()]

        # Single file mode (input and output specified)
        if len(args.files) == 2 and not args.batch:
            input_file, output_file = args.files

            # If multiple qualities specified, ignore output_file and use multiple quality mode
            if len(qualities) > 1:
                if RICH_AVAILABLE:
                    compressor.console.print(f"🎯 Multiple qualities detected: {', '.join(qualities)}", style="cyan")
                    compressor.console.print(f"📁 Output file '{output_file}' ignored, using quality-based naming", style="yellow")
                else:
                    print(f"🎯 Multiple qualities detected: {', '.join(qualities)}")
                    print(f"📁 Output file '{output_file}' ignored, using quality-based naming")

                successful, failed = compressor.compress_video_multiple_qualities(input_file, qualities, args.gpu)
                if RICH_AVAILABLE:
                    compressor.console.print(f"\n📊 Results: {len(successful)} successful, {len(failed)} failed", style="bold green")
                else:
                    print(f"\n📊 Results: {len(successful)} successful, {len(failed)} failed")
                return 0 if len(failed) == 0 else 1
            else:
                success = compressor.compress_video(input_file, output_file, qualities[0], args.gpu)
                return 0 if success else 1

        # Batch processing mode
        elif args.batch or len(args.files) > 2:
            if not args.output_dir:
                output_dir = "compressed_videos"
                if RICH_AVAILABLE:
                    compressor.console.print(f"📁 No output directory specified, using: {output_dir}", style="yellow")
                else:
                    print(f"📁 No output directory specified, using: {output_dir}")
            else:
                output_dir = args.output_dir

            # Handle multiple qualities in batch mode
            if len(qualities) > 1:
                if RICH_AVAILABLE:
                    compressor.console.print(f"🎯 Multiple qualities detected for batch processing: {', '.join(qualities)}", style="cyan")
                else:
                    print(f"🎯 Multiple qualities detected for batch processing: {', '.join(qualities)}")

                all_successful = []
                all_failed = []

                for input_file in args.files:
                    successful, failed = compressor.compress_video_multiple_qualities(input_file, qualities, args.gpu)
                    all_successful.extend(successful)
                    all_failed.extend(failed)

                if RICH_AVAILABLE:
                    compressor.console.print(f"\n📊 Batch Results: {len(all_successful)} successful, {len(all_failed)} failed", style="bold green")
                else:
                    print(f"\n📊 Batch Results: {len(all_successful)} successful, {len(all_failed)} failed")
                return 0 if len(all_failed) == 0 else 1
            else:
                successful, failed = compressor.compress_multiple_videos(args.files, output_dir, qualities[0], args.gpu)
                return 0 if failed == 0 else 1

        # Single input file, no output specified - generate output name
        elif len(args.files) == 1:
            input_file = args.files[0]

            # If multiple qualities specified, use multiple quality mode
            if len(qualities) > 1:
                if RICH_AVAILABLE:
                    compressor.console.print(f"🎯 Multiple qualities detected: {', '.join(qualities)}", style="cyan")
                else:
                    print(f"🎯 Multiple qualities detected: {', '.join(qualities)}")

                successful, failed = compressor.compress_video_multiple_qualities(input_file, qualities, args.gpu)
                if RICH_AVAILABLE:
                    compressor.console.print(f"\n📊 Results: {len(successful)} successful, {len(failed)} failed", style="bold green")
                else:
                    print(f"\n📊 Results: {len(successful)} successful, {len(failed)} failed")
                return 0 if len(failed) == 0 else 1
            else:
                input_path = Path(input_file)
                output_file = str(input_path.with_stem(f"{input_path.stem}_compressed").with_suffix('.mp4'))

                if RICH_AVAILABLE:
                    compressor.console.print(f"📁 No output specified, using: {output_file}", style="yellow")
                else:
                    print(f"📁 No output specified, using: {output_file}")

                success = compressor.compress_video(input_file, output_file, qualities[0], args.gpu)
                return 0 if success else 1

        else:
            if RICH_AVAILABLE:
                compressor.console.print("❌ No input files specified. Use --help for usage information.", style="bold red")
            else:
                print("❌ No input files specified. Use --help for usage information.")
            parser.print_help()
            return 1

    except FileNotFoundError as e:
        if RICH_AVAILABLE:
            compressor.console.print(f"❌ Error: {e}", style="bold red")
        else:
            print(f"❌ Error: {e}")
        return 1
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            compressor.console.print("\n⏹️ Compression cancelled by user", style="bold yellow")
        else:
            print("\n⏹️ Compression cancelled by user")
        return 1
    except Exception as e:
        if RICH_AVAILABLE:
            compressor.console.print(f"❌ Unexpected error: {e}", style="bold red")
        else:
            print(f"❌ Unexpected error: {e}")
        return 1


def run_interactive_mode(compressor):
    """Cool interactive mode with menu"""
    if not RICH_AVAILABLE:
        print("\n🎮 Interactive Mode (Basic)")
        print("Note: Install 'rich' for a cooler interactive experience!")
        return run_basic_interactive_mode(compressor)

    console = compressor.console

    while True:
        console.clear()

        # Show interactive menu
        menu = Table(title="🎮 Interactive Mode", show_header=False, box=None)
        menu.add_column("Option", style="cyan", width=3)
        menu.add_column("Description", style="white")

        menu.add_row("1.", "🎬 Compress single video")
        menu.add_row("2.", "📚 Batch compress multiple videos")
        menu.add_row("3.", "⚙️ Quality settings info")
        menu.add_row("4.", "📊 File size calculator")
        menu.add_row("q.", "🚪 Quit")

        console.print(menu)

        choice = input("\n🎯 Choose an option: ").strip().lower()

        if choice == '1':
            run_single_file_interactive(compressor)
        elif choice == '2':
            run_batch_interactive(compressor)
        elif choice == '3':
            show_quality_info(compressor)
        elif choice == '4':
            run_size_calculator(compressor)
        elif choice in ['q', 'quit', 'exit']:
            console.print("👋 Thanks for using Ultra Cool Video Compressor!", style="bold green")
            return 0
        else:
            console.print("❌ Invalid option. Please try again.", style="bold red")
            input("Press Enter to continue...")


def run_single_file_interactive(compressor):
    """Interactive single file compression"""
    console = compressor.console

    input_file = input("📂 Enter input video path: ").strip().strip('"')
    if not Path(input_file).exists():
        console.print("❌ File not found!", style="bold red")
        input("Press Enter to continue...")
        return

    output_file = input("💾 Enter output path: ").strip().strip('"')

    console.print("\n🎯 Quality options:", style="bold cyan")
    for quality, settings in {
        "insane": "🔥 Maximum Quality (largest file)",
        "high": "✨ High Quality",
        "medium": "⚡ Balanced (recommended)",
        "low": "🚀 Speed Focus",
        "potato": "🥔 Tiny Size (smallest file)"
    }.items():
        console.print(f"  {quality}: {settings}")

    quality = input("\n🎲 Choose quality [medium]: ").strip().lower() or "medium"

    try:
        success = compressor.compress_video(input_file, output_file, quality)
        if success:
            console.print("\n🎉 Compression completed successfully!", style="bold green")
        else:
            console.print("\n❌ Compression failed.", style="bold red")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="bold red")

    input("\nPress Enter to continue...")


def run_batch_interactive(compressor):
    """Interactive batch processing"""
    console = compressor.console

    console.print("📚 Batch Processing Mode", style="bold cyan")
    console.print("Enter video file paths (one per line, empty line to finish):")

    input_files = []
    while True:
        file_path = input(f"📁 File {len(input_files)+1}: ").strip().strip('"')
        if not file_path:
            break
        if Path(file_path).exists():
            input_files.append(file_path)
        else:
            console.print("⚠️ File not found, skipping...", style="yellow")

    if not input_files:
        console.print("❌ No valid files provided.", style="bold red")
        input("Press Enter to continue...")
        return

    output_dir = input("📂 Output directory [./compressed]: ").strip() or "./compressed"
    quality = input("🎲 Quality [medium]: ").strip().lower() or "medium"

    try:
        successful, failed = compressor.compress_multiple_videos(input_files, output_dir, quality)
        console.print(f"\n📊 Results: {successful} successful, {failed} failed", style="bold green")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="bold red")

    input("\nPress Enter to continue...")


def show_quality_info(compressor):
    """Show detailed quality settings information"""
    console = compressor.console

    quality_table = Table(title="🎯 Quality Settings Guide", show_header=True, header_style="bold magenta")
    quality_table.add_column("Quality", style="cyan")
    quality_table.add_column("Description", style="green")
    quality_table.add_column("Best For", style="yellow")
    quality_table.add_column("File Size", style="red")

    quality_table.add_row("🔥 Insane", "Maximum quality, slow compression", "Professional work, archival", "Largest")
    quality_table.add_row("✨ High", "High quality with good compression", "Important videos, presentations", "Large")
    quality_table.add_row("⚡ Medium", "Balanced quality and size", "Most Discord videos", "Medium")
    quality_table.add_row("🚀 Low", "Fast compression, smaller files", "Quick sharing, previews", "Small")
    quality_table.add_row("🥔 Potato", "Maximum compression", "When file size matters most", "Smallest")

    console.print(quality_table)

    tip_panel = Panel(
        "💡 Tips:\n" +
        "• Start with 'medium' for most Discord videos\n" +
        "• Use 'high' for important content\n" +
        "• Try 'potato' if file is still too large\n" +
        "• 'insane' is overkill for most social media",
        title="🎯 Pro Tips",
        border_style="cyan"
    )
    console.print(tip_panel)

    input("\nPress Enter to continue...")


def run_size_calculator(compressor):
    """Interactive file size calculator"""
    console = compressor.console

    file_path = input("📂 Enter video file path: ").strip().strip('"')
    if not Path(file_path).exists():
        console.print("❌ File not found!", style="bold red")
        input("Press Enter to continue...")
        return

    console.print("\n🔍 Analyzing video...", style="cyan")

    # Get file info
    file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
    video_info = compressor._extract_video_info(file_path)

    if video_info:
        # Create size estimates table
        estimates_table = Table(title="📊 Estimated Compressed Sizes", show_header=True, header_style="bold green")
        estimates_table.add_column("Quality", style="cyan")
        estimates_table.add_column("Estimated Size", style="yellow")
        estimates_table.add_column("Discord Ready", style="green")

        # Rough size estimates based on quality settings
        size_multipliers = {
            "insane": 0.7,
            "high": 0.5,
            "medium": 0.3,
            "low": 0.2,
            "potato": 0.12
        }

        for quality, multiplier in size_multipliers.items():
            estimated_size = file_size_mb * multiplier
            discord_ready = "✅ Yes" if estimated_size <= 25 else "❌ No"
            estimates_table.add_row(quality.title(), f"{estimated_size:.1f} MB", discord_ready)

        console.print(f"\n📁 Original file: {file_size_mb:.1f} MB")
        console.print(estimates_table)

        note_panel = Panel(
            "📝 Note: These are rough estimates based on typical compression ratios.\n" +
            "Actual results may vary depending on video content, resolution, and duration.",
            title="⚠️ Disclaimer",
            border_style="yellow"
        )
        console.print(note_panel)
    else:
        console.print("❌ Could not analyze video file.", style="bold red")

    input("\nPress Enter to continue...")


def run_basic_interactive_mode(compressor):
    """Basic interactive mode for when rich is not available"""
    while True:
        print("\n" + "="*50)
        print("🎮 INTERACTIVE MODE")
        print("="*50)
        print("1. 🎬 Compress single video")
        print("2. 📚 Batch compress multiple videos")
        print("3. ⚙️ Quality settings info")
        print("q. 🚪 Quit")

        choice = input("\n🎯 Choose an option: ").strip().lower()

        if choice == '1':
            input_file = input("📂 Enter input video path: ").strip().strip('"')
            output_file = input("💾 Enter output path: ").strip().strip('"')
            quality = input("🎲 Quality [medium]: ").strip().lower() or "medium"

            try:
                success = compressor.compress_video(input_file, output_file, quality)
                print("\n🎉 Done!" if success else "\n❌ Failed!")
            except Exception as e:
                print(f"\n❌ Error: {e}")

        elif choice == '2':
            print("📚 Enter video files (empty line to finish):")
            files = []
            while True:
                file_path = input(f"File {len(files)+1}: ").strip().strip('"')
                if not file_path:
                    break
                files.append(file_path)

            if files:
                output_dir = input("Output directory [./compressed]: ").strip() or "./compressed"
                quality = input("Quality [medium]: ").strip().lower() or "medium"
                try:
                    successful, failed = compressor.compress_multiple_videos(files, output_dir, quality)
                    print(f"\n📊 Results: {successful} successful, {failed} failed")
                except Exception as e:
                    print(f"\n❌ Error: {e}")

        elif choice == '3':
            print("\n🎯 Quality Settings:")
            print("  insane: 🔥 Maximum quality (largest files)")
            print("  high:   ✨ High quality")
            print("  medium: ⚡ Balanced (recommended)")
            print("  low:    🚀 Speed focus (smaller files)")
            print("  potato: 🥔 Maximum compression (smallest)")

        elif choice in ['q', 'quit', 'exit']:
            print("👋 Thanks for using Ultra Cool Video Compressor!")
            return 0
        else:
            print("❌ Invalid option")

        input("\nPress Enter to continue...")


if __name__ == '__main__':
    if not RICH_AVAILABLE:
        print("💡 Install 'rich' and 'pyfiglet' for the full cool experience:")
        print("   pip install rich pyfiglet")
        print()

    sys.exit(main())