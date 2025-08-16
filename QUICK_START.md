## Quick Start

This project scrapes Skool classroom collections and saves each lesson’s content. By default it extracts metadata (video URLs, text, links) and downloads images. Actual video files are NOT downloaded unless you opt in.

### What you’ll get
- All lessons found in a classroom collection are iterated automatically
- A markdown file per lesson with content, links, and the video URL (no video download by default)
- Organized folders under `Communities/`

### Prerequisites
- Windows 10/11 (or macOS/Linux)
- Python 3.9+
- Google Chrome installed
- Install dependencies in a terminal at the project root:

```bash
pip install -r requirements.txt
```

### Primary script (multi‑lesson)
- Script: `skool_content_extractor.py`
- Behavior:
  - Logs in to Skool
  - Enumerates all lessons in the classroom sidebar
  - Visits each lesson via its `?md=` URL
  - Extracts video URL, text, links, and images
  - Saves a markdown file per lesson

### Run it (example)
- Example classroom URL (New Society):
  - [https://www.skool.com/new-society/classroom/5d7e39c5?md=7c8fdc96f18e4cf6a5fa21d523380c64](https://www.skool.com/new-society/classroom/5d7e39c5?md=7c8fdc96f18e4cf6a5fa21d523380c64)

Run the scraper:

```bash
python skool_content_extractor.py "https://www.skool.com/new-society/classroom/5d7e39c5?md=7c8fdc96f18e4cf6a5fa21d523380c64"
```

Optional flags:
- `--email you@example.com --password your_password` to pass credentials explicitly
- `--download-videos` if you want to download video files (otherwise only URLs are saved)

On Windows, you can also run the helper script and paste the URL when prompted:

```bat
run_extractor.bat
```

### Output Structure
- Files are saved under `Communities/<Community Name (slug)>/`
  - **🆕 HIERARCHICAL LESSONS** - organized by Skool's structure:
    ```
    Communities/New Society (new-society)/
    ├── Code with AI/
    │   ├── Ultimate Codex Guide/
    │   │   ├── 1. Pro Codex setup.md
    │   │   ├── 2. Github fundamentals.md
    │   │   └── 3. David's Codex workflow.md
    │   └── Claude Code Mastery/
    │       ├── 1. How to set up Claude Code.md
    │       └── 2. maximizing coding produ.md
    ├── images/ - downloaded lesson images
    └── videos/ - used only if `--download-videos` is provided
    ```
  - **Automatic organization** - matches Skool's 3-level structure (Main Section → Sub-section → Lessons)

### Video Extraction Features
- ✅ **Enhanced video detection** - clicks video players to trigger loading
- ✅ **Multi-platform support** - YouTube, Vimeo, Loom, Wistia
- ✅ **Prevents duplicate videos** - filters out cached/header videos
- ✅ **Debug mode** - saves JSON data for troubleshooting

### Wistia-only lessons (new fallback)
- Some Skool lessons expose Wistia videos via Skool links like `?wvideo=ID` or class markers such as `wistia_async_{ID}` without an immediate iframe.
- The extractor now detects these and canonicalizes to `https://fast.wistia.net/embed/iframe/{ID}`.
- This fallback only triggers on lessons that need it; YouTube/Vimeo/Loom behavior remains unchanged.

### View HLS quickly (optional)
- If a lesson produces a Wistia HLS URL (m3u8), you can preview it with VLC:
  ```bat
  vlc "https://fast.wistia.com/embed/medias/3g1szfgexr.m3u8"
  ```
- Or open the canonical iframe URL in a browser:
  - https://fast.wistia.net/embed/iframe/3g1szfgexr

### Tips to scrape ALL lessons
- Make sure you pass a classroom collection URL (the page with the left sidebar of lessons), not a single direct lesson URL.
- The script auto‑expands sections and maps titles to their `md` hashes to visit each lesson.
- Summary stats are printed at the end: processed, skipped, and failed lessons.

### Troubleshooting
- Only one lesson extracted:
  - Verify you used the classroom collection URL (with `/classroom/<id>` and an `md=` parameter)
  - Use the example above and confirm it lists multiple lessons in the left sidebar
- Login issues:
  - Double‑check email/password (or omit flags to use defaults in script config)
  - Ensure your account has access to the community
  - If you encounter 2FA/CAPTCHA, try an interactive (non‑headless) run and stay logged in
- Chrome/driver issues:
  - Ensure Chrome is installed and up to date
  - Re‑run `pip install -r requirements.txt`

## 🧩 Downloads for Wistia/others

### Install tools
```bat
python -m pip install --user yt-dlp
```
If prompted for ffmpeg:
```bat
winget install -e --id Gyan.FFmpeg
```

### Single lesson (download video)
```bat
python extract_single_with_youtube_fix.py "<LESSON_URL>" --download-video
```

### Full classroom (download videos)
```bat
python skool_content_extractor.py "<CLASSROOM_URL>" --download-videos
```

### Direct download examples (optional)
- Wistia iframe (yt-dlp selects best H.264 and remuxes to mp4):
```bat
python -m yt_dlp "https://fast.wistia.net/embed/iframe/3g1szfgexr" -S "res:1080,codec:h264" --remux-video mp4 -o "Lesson Title.%(ext)s"
```
- Wistia HLS master (fallback):
```bat
python -m yt_dlp "https://fast.wistia.com/embed/medias/3g1szfgexr.m3u8" --merge-output-format mp4 -o "Lesson Title.%(ext)s"
```
- ffmpeg remux (no re-encode; fast if compatible):
```bat
ffmpeg -i "https://fast.wistia.com/embed/medias/3g1szfgexr.m3u8" -c copy -bsf:a aac_adtstoasc -movflags +faststart "Lesson Title.mp4"
```

## 📚 Examples
- Classroom (New Society):
  - https://www.skool.com/new-society/classroom/4b8fd56f?md=ec398496f57f4067a162b3db5abd0e8f
- Wistia HLS (from a detected lesson):
  - https://fast.wistia.com/embed/medias/3g1szfgexr.m3u8

## 📁 All Available Scripts

### 🚀 **Main Scripts** (Recommended)

#### `skool_content_extractor.py` ⭐ **PRIMARY**
- **Purpose**: Extract ALL lessons from a Skool classroom collection
- **Features**: Enhanced video detection, multi-platform support, organized output
- **Usage**: `python skool_content_extractor.py "https://www.skool.com/..."`
- **Output**: `Communities/<Community Name>/lessons/` with markdown files per lesson

#### `cleanup_scraper.py` 🧹 **UTILITY**
- **Purpose**: Clean up previous scraping data to prevent conflicts
- **Features**: Backup, restore, selective cleanup by date/size
- **Usage**: `python cleanup_scraper.py` (interactive menu)
- **When to use**: Before starting new scrapes or when organizing data

### 🎯 **Single Lesson Scripts**

#### `extract_single_with_youtube_fix.py`
- **Purpose**: Extract one specific lesson with enhanced video detection
- **Features**: Hierarchical structure, single lesson focus
- **Usage**: Modify URL in script and run
- **When to use**: Testing or extracting just one lesson

### 🔧 **Legacy/Alternative Scripts**

#### `Master Skool Scrapper/skool_video_scraper/main.py`
- **Purpose**: Original video-focused scraper with yt-dlp integration
- **Features**: Video downloads, session management, duplicate detection
- **Usage**: Run from `Master Skool Scrapper/skool_video_scraper/` directory
- **When to use**: When you specifically need video file downloads

#### `Master Skool Scrapper/skool_video_scraper/complete_n8n_scraper.py`
- **Purpose**: Specialized scraper for N8N workflow content
- **Features**: Image extraction, text parsing, workflow-specific logic
- **Usage**: For N8N automation workflow classrooms
- **Output**: Organized workflow descriptions and images

#### `Master Skool Scrapper/skool_video_scraper/n8n_scraper.py`
- **Purpose**: Basic N8N content scraper
- **Features**: Simple image and text extraction
- **Usage**: Basic N8N workflow scraping

### 📂 **Backup/Archive Scripts** (`restore_point_backup/`)

#### `extract_all_may_2025_complete.py`
- **Purpose**: Extract all lessons from May 2025 specifically
- **Features**: Month-specific filtering, comprehensive extraction
- **Usage**: Historical/backup extraction for specific time periods

#### `extract_may_2025_lessons.py`
- **Purpose**: Simplified May 2025 lesson extractor
- **Features**: Basic May 2025 lesson extraction
- **Usage**: Alternative May 2025 extraction method

#### `extract_single_lesson.py`
- **Purpose**: Basic single lesson extraction (backup version)
- **Features**: Simple single lesson scraping
- **Usage**: Basic single lesson extraction

### 🖱️ **Windows Helper Scripts** (.bat files)

#### `run_extractor.bat` ⭐ **EASY START**
- **Purpose**: User-friendly launcher for main scraper
- **Features**: Interactive URL input, automatic script execution
- **Usage**: Double-click to run, paste URL when prompted

#### `run_cleanup.bat` 🧹
- **Purpose**: Windows launcher for cleanup tool
- **Features**: Automatic Python detection, error handling
- **Usage**: Double-click to run cleanup tool

#### `run_single_lesson.bat`
- **Purpose**: Windows launcher for single lesson extraction
- **Usage**: Double-click and follow prompts

#### `run_sops_extractor.bat`
- **Purpose**: Specialized launcher for specific extraction tasks
- **Usage**: Context-specific extraction scenarios

## 🎯 **Which Script Should I Use?**

### For Most Users:
1. **`run_extractor.bat`** (Windows) - Easiest way to start
2. **`python skool_content_extractor.py "URL"`** (All platforms) - Direct command

### For Specific Needs:
- **Clean old data**: `run_cleanup.bat` or `python cleanup_scraper.py`
- **Single lesson only**: `extract_single_with_youtube_fix.py`
- **Video downloads**: `Master Skool Scrapper/skool_video_scraper/main.py`
- **N8N workflows**: `Master Skool Scrapper/skool_video_scraper/complete_n8n_scraper.py`

### Notes
- By default, videos are NOT downloaded; only their URLs are saved in each lesson's markdown. Add `--download-videos` to fetch video files.
- Be respectful of Skool's Terms and the content owner's policies. Scrape only content you have permission to access.


