# 🧹 Skool Scraper Cleanup System

**Comprehensive cleanup tool to manage previous scraping data and prevent conflicts**

## 🎯 Why Use the Cleanup System?

### Problems Solved:
- **Prevents Confusion** - Clean separation between different scraping sessions
- **Avoids Conflicts** - No mixing of old and new community data  
- **Saves Storage** - Remove outdated or unwanted extractions
- **Improves Organization** - Keep only the content you need
- **Reduces Errors** - Clean slate for each new scraping operation

---

## 🚀 Quick Start

### Windows Users (Recommended):
```bash
# Run the cleanup tool
run_cleanup.bat

# Or run main extractor (includes cleanup option)
run_extractor.bat
```

### Command Line:
```bash
# Interactive cleanup mode
python cleanup_scraper.py

# Auto-clean all communities
python cleanup_scraper.py --auto-clean

# Clean communities older than 7 days
python cleanup_scraper.py --days 7

# Clean specific community
python cleanup_scraper.py --community "AI Money Lab"
```

---

## 🎛️ Cleanup Options

### 1. **Interactive Mode** (Recommended)
- Visual display of all communities with stats
- Multiple cleanup strategies
- Safe backup creation
- Step-by-step guidance

### 2. **Clean All Communities**
- Removes all existing community folders
- Creates automatic backup
- Requires confirmation for safety

### 3. **Selective Cleanup**
- Choose specific communities to remove
- See size and file counts before cleaning
- Flexible selection (numbers, ranges, or 'all')

### 4. **Date-Based Cleanup**
- Remove communities older than X days
- Useful for regular maintenance
- Preserves recent work automatically

### 5. **Size-Based Cleanup**
- Target largest communities first
- Free up storage efficiently
- Ideal when disk space is limited

---

## 🛡️ Safety Features

### Automatic Backups:
- **Every cleanup creates a backup** (unless disabled)
- Backups stored in `cleanup_backups/` folder
- Compressed ZIP format for efficiency
- Timestamped for easy identification

### Whitelist Protection:
```
Protected folders (never deleted):
- sample_output/
- Master Skool Scrapper/
- SkoolContentExtractor/
- restore_point_backup/
- __pycache__/
- .git/
- cleanup_backups/
```

### Confirmation Prompts:
- **Double confirmation** for major operations
- **Clear warnings** about what will be deleted
- **Size and file count** displayed before cleanup
- **Cancel anytime** without changes

---

## 📊 Community Analysis

The cleanup tool provides detailed stats for each community:

```
📊 FOUND 3 COMMUNITY FOLDERS:
--------------------------------------------------------------------------------
#   Community Name                      Size       Files    Modified    
--------------------------------------------------------------------------------
1   AI Money Lab                        45.2MB     23       2024-08-15  
2   New Society                         12.8MB     8        2024-08-14  
3   AI Automation Society               67.1MB     45       2024-08-10  
--------------------------------------------------------------------------------
TOTAL                                   125.1MB    76       
```

**Stats Include:**
- **Size:** Total folder size in MB
- **Files:** Count of lessons, videos, and images
- **Modified:** Last modification date
- **Content breakdown** by type

---

## 💾 Backup & Restore System

### Automatic Backups:
- Created before every cleanup operation
- Named with timestamp: `backup_20240815_143022.zip`
- Stored in `cleanup_backups/` folder
- Contains complete community structures

### Manual Backup:
```bash
# Backup specific communities before manual cleanup
python cleanup_scraper.py
# Choose option 5: View backups
# Choose option 6: Restore from backup
```

### Restore Process:
1. **View available backups** with dates and sizes
2. **Select backup** to restore from
3. **Confirmation prompt** (overwrites existing data)
4. **Automatic extraction** to Communities folder

---

## 🔗 Integration with Main Scripts

### Automatic Integration:
Both main scraper scripts now include cleanup integration:

**Full Community Extractor:**
```bash
python skool_content_extractor.py
# Automatically detects existing communities
# Offers cleanup options before extraction
```

**Single Lesson Extractor:**
```bash
python extract_single_with_youtube_fix.py  
# Offers community-specific cleanup
# Allows adding to existing or cleaning first
```

### Batch File Integration:
- `run_extractor.bat` - Shows cleanup reminder
- `run_single_lesson.bat` - Includes cleanup tip
- `run_cleanup.bat` - Dedicated cleanup launcher

---

## ⚙️ Command Line Options

### Basic Usage:
```bash
python cleanup_scraper.py                    # Interactive mode
```

### Advanced Options:
```bash
python cleanup_scraper.py --auto-clean       # Clean all (with backup)
python cleanup_scraper.py --days 7           # Clean older than 7 days
python cleanup_scraper.py --community "Name" # Clean specific community
python cleanup_scraper.py --no-backup        # Skip backup creation
```

### Combining Options:
```bash
# Clean communities older than 3 days without backup
python cleanup_scraper.py --days 3 --no-backup

# Clean specific community with backup (default)
python cleanup_scraper.py --community "AI Money Lab"
```

---

## 📁 File Structure

### After Installation:
```
Skool scrapper both images videos/
├── cleanup_scraper.py           # Main cleanup script
├── run_cleanup.bat             # Windows launcher
├── cleanup_config.json         # Configuration (auto-created)
├── cleanup_backups/            # Backup storage
│   ├── backup_20240815_143022.zip
│   └── backup_20240814_091533.zip
├── Communities/                # Target for cleanup
│   ├── AI Money Lab/
│   ├── New Society/
│   └── AI Automation Society/
└── [existing scraper files]
```

---

## 🔧 Configuration

### Whitelist Customization:
Edit `cleanup_config.json` to modify protected folders:

```json
{
  "whitelist": [
    "sample_output",
    "Master Skool Scrapper", 
    "my_important_folder",
    "custom_scripts"
  ],
  "last_cleanup": "2024-08-15T14:30:22"
}
```

### Default Settings:
- **Backup creation:** Enabled by default
- **Confirmation prompts:** Always shown for safety
- **Whitelist protection:** Active for system folders
- **Compression:** ZIP format for backups

---

## 🚨 Troubleshooting

### Common Issues:

**"Permission denied" errors:**
- Close any open files in the communities
- Run as administrator if needed
- Check if folders are in use by other programs

**Backup creation fails:**
- Ensure sufficient disk space
- Check write permissions in project folder
- Verify no files are locked/in use

**Cleanup tool not found:**
- Ensure `cleanup_scraper.py` is in project root
- Check Python installation and PATH
- Try running directly: `python cleanup_scraper.py`

### Recovery:
If something goes wrong:
1. **Check backup folder** for recent backups
2. **Use restore function** in cleanup tool
3. **Manual restore** by extracting backup ZIP
4. **Contact support** with error details

---

## 💡 Best Practices

### Before Major Scraping:
1. **Run cleanup tool** to remove old data
2. **Review communities** to keep important ones  
3. **Create manual backup** if needed
4. **Start with clean slate** for best results

### Regular Maintenance:
- **Weekly cleanup** of old communities
- **Monthly backup review** and cleanup
- **Storage monitoring** for large extractions
- **Configuration updates** as needed

### Safety Tips:
- **Always backup** important communities first
- **Test restore process** occasionally  
- **Keep recent backups** for quick recovery
- **Verify cleanup results** before major operations

---

## 🎉 Benefits

### For Users:
- ✅ **Clean, organized** extraction environment
- ✅ **No confusion** between old and new data
- ✅ **Storage management** and optimization
- ✅ **Easy recovery** with backup system
- ✅ **Flexible options** for different needs

### For System:
- ✅ **Prevents conflicts** during extraction
- ✅ **Improves performance** with clean directories
- ✅ **Reduces errors** from stale data
- ✅ **Maintains consistency** across sessions
- ✅ **Enables reliable** repeated extractions

---

**🚀 Ready to start? Run `run_cleanup.bat` or `python cleanup_scraper.py` to begin!**