# 🔄 Developer Handoff - Skool Scraper Project

## 📋 **Project Overview**
Skool classroom content scraper that extracts lessons, videos, images, and text content from Skool communities. The scraper navigates through lessons, extracts video URLs (without downloading by default), and organizes content in a hierarchical folder structure.

## ✅ **What's Been Successfully Implemented**

### 1. **Hierarchical Folder Structure** ✅ WORKING
- **Problem Solved**: Lessons were being dumped into a flat `lessons/` folder
- **Solution Implemented**: Automatic 3-level hierarchy matching Skool's structure
- **Result**: 
  ```
  Communities/New Society (new-society)/
  ├── Code with AI/
  │   ├── Ultimate Codex Guide/
  │   │   ├── 1. Pro Codex setup.md
  │   │   └── 2. Github fundamentals.md
  └── Claude Code Mastery/
      └── 1. How to set up Claude Code.md
  ```
- **Key Functions Added**:
  - `extract_course_hierarchy()` - extracts structure from JSON
  - `create_hierarchical_lesson_directories()` - creates nested folders
  - `find_lesson_hierarchy_path()` - maps lessons to correct paths

### 2. **Enhanced Video Extraction** ✅ WORKING
- **Multi-platform Support**: YouTube, Vimeo, Loom, Wistia
- **Multiple Extraction Methods**: JSON parsing, iframe scanning, video player clicking, legacy fallback
- **Enhanced Detection**: Clicks play buttons to trigger video loading
- **Key Functions**: `extract_video_url()`, `click_video_player_and_extract()`, `scan_video_iframes_filtered()`

### 3. **Content Organization** ✅ WORKING
- **Markdown Generation**: Rich lesson content with video URLs, images, links
- **Image Downloads**: Automatic image extraction and organization
- **Community Detection**: Extracts clean community names from page content

## 🚨 **PERSISTENT ISSUE: Duplicate Video Bug**

### **The Problem**
Despite multiple attempts to fix it, the same video URL appears across multiple lessons that should have different videos.

### **Current Manifestation**
- **Duplicate Video ID**: `65GvYDdzJWU`
- **URL**: `https://youtu.be/65GvYDdzJWU`
- **Appears In**: THE GRAND VISION, v55, v56, v57, v60, and likely more lessons
- **Should Be**: Each lesson should have its own unique video or "No video found"

### **Root Cause Analysis**
The issue stems from **cached/persistent video elements** in the DOM that get picked up by multiple extraction methods:

1. **Header/Navigation Videos**: Some videos exist in the page header/navigation that persist across all lesson pages
2. **JavaScript State**: Video players might retain state between page navigations
3. **Fallback Logic**: When lesson-specific videos aren't found, fallback methods pick up these persistent elements

### **Attempted Solutions & Why They Failed**

#### ❌ **Attempt 1: Individual Method Filtering**
- **What Was Done**: Added blacklists to specific extraction methods
- **Files Modified**: `extract_youtube_url_legacy()`, `scan_video_iframes_filtered()`
- **Why It Failed**: Cached videos found alternative extraction paths

#### ❌ **Attempt 2: Position-Based Filtering**
- **What Was Done**: Skip iframes positioned too high on page (Y < 200px)
- **Why It Failed**: Cached videos might not be in header positions

#### ❌ **Attempt 3: Container-Specific Scanning**
- **What Was Done**: Only scan within lesson content containers
- **Why It Failed**: Cached videos might be injected into content areas

#### ❌ **Attempt 4: Centralized Validation (Current)**
- **What Was Done**: Created `is_valid_lesson_video()` function with global blacklist
- **Implementation**: ALL extraction methods must validate through this function
- **Blacklist**: `["YTrIwmIdaJI", "UDcrRdfB0x8", "7snrj0uEaDw", "65GvYDdzJWU"]`
- **Why It's Still Failing**: Unknown - needs investigation

## 🔍 **Technical Investigation Needed**

### **Key Questions for Next Developer**

1. **Where is the cached video coming from?**
   - Is it in the page HTML source?
   - Is it injected by JavaScript after page load?
   - Is it in the `__NEXT_DATA__` JSON structure?

2. **Which extraction method is finding it?**
   - JSON parsing (`extract_from_next_data()`)?
   - Iframe scanning (`scan_video_iframes_filtered()`)?
   - Video player clicking (`click_video_player_and_extract()`)?
   - Legacy page source scanning (`extract_youtube_url_legacy()`)?

3. **Is the validation function being called?**
   - Are the console messages `🚫 BLOCKED cached video: [ID]` appearing?
   - Is the centralized validation being bypassed somehow?

### **Debugging Tools Available**

1. **`debug_lesson_data.json`** - Saves lesson JSON structure for analysis
2. **`debug_hierarchy.json`** - Saves course hierarchy data
3. **`find_duplicate_videos.py`** - Analyzes existing scraped content for duplicates
4. **Console Logging** - Extensive logging throughout extraction process

### **Investigation Steps**

1. **Add More Logging**: Insert debug prints in EVERY extraction method to see which one is returning the duplicate
2. **Check JSON Structure**: Examine `debug_lesson_data.json` to see if duplicate video is in the raw data
3. **Test Individual Methods**: Temporarily disable extraction methods one by one to isolate the source
4. **Browser Inspector**: Manually inspect the lesson pages to see where the cached video elements are located

## 📁 **Key Files to Understand**

### **Main Files**
- **`skool_content_extractor.py`** - Primary scraper with all functionality
- **`QUICK_START.md`** - User documentation and usage instructions

### **Configuration**
- **Credentials**: Provide via environment variables `SKOOL_EMAIL` and `SKOOL_PASSWORD`, or pass with `--email` and `--password` CLI flags.
- **Test URL**: `https://www.skool.com/new-society/classroom/5d7e39c5`

### **Key Functions to Debug**
```python
# Main extraction orchestrator
def extract_video_url(driver)

# Individual extraction methods
def extract_from_next_data(driver)
def click_video_player_and_extract(driver)  
def scan_video_iframes_filtered(driver)
def extract_youtube_url_legacy(driver)

# Validation (should be blocking duplicates)
def is_valid_lesson_video(video_url)
```

## 🎯 **Recommended Next Steps**

### **Immediate Actions**
1. **Run with Enhanced Logging**: Add debug prints to identify which extraction method is finding the duplicate
2. **Test Validation Function**: Verify `is_valid_lesson_video()` is actually being called
3. **Manual Page Inspection**: Use browser dev tools to find where `65GvYDdzJWU` exists in the DOM

### **Potential Solutions to Try**

#### **Option 1: More Aggressive Filtering**
- Clear browser cache/cookies between lessons
- Wait longer between page navigations
- Force page refresh before each extraction

#### **Option 2: Lesson-Specific Validation**
- Extract lesson title/ID and validate video belongs to that specific lesson
- Cross-reference video with lesson metadata

#### **Option 3: Complete Method Isolation**
- Disable all extraction methods except JSON parsing
- If that works, re-enable methods one by one to find the culprit

#### **Option 4: Session Management**
- Use separate browser instances for each lesson
- Clear JavaScript state between extractions

## 🚀 **What's Working Well**
- ✅ Login and authentication
- ✅ Lesson discovery and navigation  
- ✅ Content extraction (text, images, links)
- ✅ Hierarchical folder organization
- ✅ Multi-platform video URL detection (when not duplicate)
- ✅ Markdown generation and file organization

## 📊 **Success Metrics**
When fixed, you should see:
- Each lesson has a unique video URL OR "No video found"
- Console shows `🚫 BLOCKED cached video: [ID]` for known duplicates
- No duplicate video IDs appear across multiple lessons

## 🔗 **Resources**
- **Test Community**: New Society (new-society)
- **Sample Lesson**: `md=b9c4beae12784a7f9cc2460c43060362`
- **Debug Files**: Generated in project root during execution
- **Documentation**: All `.md` files in project root contain implementation details

---

**Good luck! The core functionality is solid - just need to solve this persistent caching issue.** 🚀


