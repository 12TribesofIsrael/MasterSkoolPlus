# 🚀 Ultimate Skool Scraper V5.1 - Production Ready

A powerful, feature-rich content extraction tool for Skool.com communities. **Now with advanced video detection, hierarchical organization, and comprehensive cleanup system.**

## ✨ Latest Breakthroughs (V5.1)

### 🎥 **Advanced Video Detection Pipeline**
- **Enhanced JSON Extraction** - Searches multiple paths in `__NEXT_DATA__`
- **Universal Iframe Scanning** - Detects React players and traditional iframes
- **🆕 Safe Video Thumbnail Clicking** - Clicks video thumbnails safely without page navigation
- **🆕 Modal/Popup Video Player Detection** - Finds videos in modal overlays
- **🆕 Custom Video Player Detection** - Handles red play buttons and custom players
- **🆕 Wistia `wvideo`/Class-based Detection** - Extracts Wistia IDs from URL query params and `wistia_async_*` classes
- **🆕 Overlay Dismissal** - Automatically dismisses "click for sound" overlays
- **Legacy YouTube Extraction** - Backward compatibility fallback

### 🗂️ **Hierarchical Folder Structure**
Organizes content exactly like Skool's structure:
```
Communities/
├── Community Name (slug)/
│   ├── lessons/
│   │   ├── Lesson 1.md
│   │   ├── Lesson 2.md
│   │   └── ...
│   ├── images/
│   └── videos/
```

### 🧹 **Comprehensive Cleanup System**
- **Automatic Backups** - Creates timestamped backups before cleaning
- **Selective Cleaning** - Remove specific communities, date ranges, or size-based
- **Restore Capability** - Restore from any backup point
- **Smart Detection** - Identifies and manages duplicate content

### 🔧 **Enhanced Features**
- **State Isolation** - Clears browser storage between lessons
- **Duplicate Prevention** - Centralized validation system
- **URL Normalization** - Converts embed URLs to clean formats
- **Performance Logging** - Detailed extraction metrics
- **Error Recovery** - Graceful handling of network issues

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/12TribesofIsrael/masterscraper.git
cd masterscraper
pip install -r requirements.txt
```

### Basic Usage

#### Configure credentials
Create a `.env` file in the project root or export env vars:
```bash
SKOOL_EMAIL="your@email"
SKOOL_PASSWORD="yourpassword"
```

#### Single Lesson Extraction
```bash
python extract_single_with_youtube_fix.py "https://www.skool.com/example-community/classroom/abc123?md=xyz789"
```

#### Batch Classroom Extraction
```bash
python skool_content_extractor.py "https://www.skool.com/example-community/classroom/abc123?md=xyz789" --download-videos
```

#### Cleanup Previous Extractions
```bash
python cleanup_scraper.py
```

## 📋 Features

### 🎯 **Content Extraction**
- ✅ **Text Content** - Full lesson text with formatting
- ✅ **Images** - All embedded images with alt text
- ✅ **Videos** - YouTube, Vimeo, Loom, Wistia, and custom players
- ✅ **Links** - External and internal links
- ✅ **Metadata** - Lesson titles, dates, and descriptions

### 🎥 **Video Platform Support**
- **YouTube** - Direct and embed URLs
- **Vimeo** - Standard and private videos
- **Loom** - Screen recordings and presentations
- **Wistia** - Business video hosting (including `wvideo` query params)
- **Custom Players** - Red play buttons and modal overlays

### 🗂️ **Organization**
- **Hierarchical Structure** - Matches Skool's community/lesson organization
- **Clean Naming** - Removes special characters and spaces
- **Metadata Preservation** - Maintains lesson context and relationships

### 🛠️ **Management Tools**
- **Cleanup System** - Remove old extractions with backup/restore
- **Duplicate Detection** - Prevents saving redundant content
- **Progress Tracking** - Real-time extraction status
- **Error Handling** - Graceful failure recovery

## 📖 Documentation

- **[PROJECT_STATUS_UPDATE.md](PROJECT_STATUS_UPDATE.md)** - Latest breakthroughs and fixes
- **[VIDEO_EXTRACTION_FIX.md](VIDEO_EXTRACTION_FIX.md)** - Video detection enhancements
- **[QUICK_START.md](QUICK_START.md)** - Step-by-step usage guide
- **[CLEANUP_SYSTEM_README.md](CLEANUP_SYSTEM_README.md)** - Cleanup system documentation

## 🎯 Example Output

### Sample Lesson Structure
```
Communities/
└── Example Community (example-community)/
    ├── lessons/
    │   ├── Introduction to Web Development.md
    │   ├── HTML Basics.md
    │   └── CSS Fundamentals.md
    ├── images/
    │   ├── web-dev-workflow.png
    │   └── code-example.png
    └── videos/
        ├── intro-video.mp4
        └── tutorial-session.mp4
```

### Lesson Content Format
```markdown
# Introduction to Web Development

**📅 Date:** 2024-01-15  
**⏱️ Duration:** 45 minutes  

## 📝 Lesson Content
[Extracted lesson text with full formatting]

## 🎥 Video Content
**🎥 Video (YouTube):** https://www.youtube.com/watch?v=example

## 📸 Images
![Description](image-url)

## 🔗 Links
[External resources and references]
```

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set custom output directory
EXTRACTION_OUTPUT_DIR=./my_courses

# Optional: Set browser timeout (seconds)
BROWSER_TIMEOUT=30
```

### Browser Options
- **Chrome/Chromium** - Recommended for best compatibility
- **Firefox** - Alternative option with good support
- **Headless Mode** - Available for server environments

## 🚨 Troubleshooting

### Common Issues

#### Video Not Detected
1. **Check URL Format** - Ensure it's a valid Skool classroom URL
2. **Try Different Methods** - The pipeline uses multiple detection methods
3. **Check Network** - Ensure stable internet connection
4. **Update Dependencies** - Run `pip install -r requirements.txt`

#### Large File Downloads
- **Wistia HLS Videos** - Use VLC or browser for `.m3u8` files
- **Conversion to MP4** - Use `yt-dlp` or `ffmpeg` for format conversion

#### Cleanup Issues
- **Backup First** - Always create backups before major cleanup
- **Check Permissions** - Ensure write access to directories
- **Restore Option** - Use restore feature if needed

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Security
- Do not commit real credentials. Use environment variables (`SKOOL_EMAIL`, `SKOOL_PASSWORD`), a local `.env` file, or the batch scripts which prompt if unset.

## 🙏 Acknowledgments

- **Skool.com** - For providing the platform
- **Selenium** - For browser automation capabilities
- **yt-dlp** - For video downloading functionality
- **Open Source Community** - For continuous improvements

---

**⭐ Star this repository if you find it helpful!**

*Last updated: January 2025 - V5.1 Production Release*