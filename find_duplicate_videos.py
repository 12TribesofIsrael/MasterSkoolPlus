#!/usr/bin/env python3
"""
Diagnostic script to find duplicate video URLs in scraped lessons
"""

import os
import re
from collections import Counter

def find_duplicate_videos():
    """Find duplicate video URLs in all scraped lesson files"""
    
    lessons_dir = "Communities"
    video_urls = []
    lesson_files = []
    
    # Walk through all lesson files
    for root, dirs, files in os.walk(lessons_dir):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                lesson_files.append(filepath)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Extract video URLs from markdown
                        video_patterns = [
                            r'🎥 Video \([^)]+\): (https://[^\s)]+)',
                            r'Video: (https://[^\s)]+)',
                            r'(https://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]{11})',
                            r'(https://[^\s]+(?:youtube|vimeo|loom|wistia)[^\s]*)'
                        ]
                        
                        for pattern in video_patterns:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                video_urls.append((match, filepath))
                                
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
                    continue
    
    if not video_urls:
        print("No video URLs found in scraped lessons")
        return
    
    print(f"📊 Analysis of {len(video_urls)} video URLs from {len(lesson_files)} lessons:")
    print("=" * 80)
    
    # Count occurrences of each URL
    url_counts = Counter([url for url, _ in video_urls])
    
    # Find duplicates
    duplicates = {url: count for url, count in url_counts.items() if count > 1}
    
    if duplicates:
        print(f"🚨 DUPLICATE VIDEOS FOUND ({len(duplicates)} unique duplicates):")
        print("-" * 80)
        
        for url, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True):
            print(f"\\n🔄 {count}x DUPLICATES: {url}")
            
            # Extract video ID for blacklist
            video_id_match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
            if video_id_match:
                video_id = video_id_match.group(1)
                print(f"   📋 Video ID for blacklist: {video_id}")
            
            # Show which lessons have this duplicate
            duplicate_lessons = [filepath for vid_url, filepath in video_urls if vid_url == url]
            print(f"   📁 Found in lessons:")
            for lesson in duplicate_lessons[:5]:  # Show first 5
                lesson_name = os.path.basename(lesson).replace('.md', '')
                print(f"      - {lesson_name}")
            if len(duplicate_lessons) > 5:
                print(f"      ... and {len(duplicate_lessons) - 5} more")
        
        # Generate blacklist code
        print(f"\\n🛠️ BLACKLIST CODE TO ADD:")
        print("-" * 40)
        blacklist_ids = []
        for url in duplicates.keys():
            video_id_match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
            if video_id_match:
                blacklist_ids.append(f'"{video_id_match.group(1)}"  # Duplicate video')
        
        if blacklist_ids:
            print("CACHED_VIDEO_BLACKLIST = [")
            for blacklist_id in blacklist_ids:
                print(f"    {blacklist_id},")
            print("]")
    
    else:
        print("✅ NO DUPLICATE VIDEOS FOUND!")
        print("All lessons have unique video URLs.")
    
    # Show unique video count
    unique_videos = len(url_counts)
    total_videos = len(video_urls)
    print(f"\\n📈 SUMMARY:")
    print(f"   Total video URLs: {total_videos}")
    print(f"   Unique videos: {unique_videos}")
    print(f"   Duplicate instances: {total_videos - unique_videos}")

if __name__ == "__main__":
    find_duplicate_videos()

