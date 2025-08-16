#!/usr/bin/env python3
"""
🧹 Skool Scraper Cleanup Tool
Safely cleans up previous scraping data to prevent confusion and conflicts.
Includes backup, restore, and selective cleanup options.
"""

import os
import sys
import shutil
import json
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import zipfile

class SkoolScraperCleaner:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.communities_dir = self.base_dir / "Communities"
        self.backup_dir = self.base_dir / "cleanup_backups"
        self.config_file = self.base_dir / "cleanup_config.json"
        self.whitelist = self.load_whitelist()
        
    def load_whitelist(self):
        """Load protected folders that should never be deleted"""
        default_whitelist = [
            "sample_output",
            "Master Skool Scrapper",
            "SkoolContentExtractor",
            "restore_point_backup",
            "__pycache__",
            ".git",
            "cleanup_backups"
        ]
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('whitelist', default_whitelist)
            except:
                pass
        
        return default_whitelist
    
    def save_config(self):
        """Save current configuration"""
        config = {
            'whitelist': self.whitelist,
            'last_cleanup': datetime.now().isoformat()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def print_header(self):
        """Print cleanup tool header"""
        print("=" * 60)
        print("🧹 SKOOL SCRAPER CLEANUP TOOL")
        print("=" * 60)
        print("Safely clean up previous scraping data")
        print("Prevents conflicts and confusion during new scrapes")
        print("=" * 60)
    
    def scan_communities(self):
        """Scan and analyze existing community folders"""
        if not self.communities_dir.exists():
            return {}
        
        communities = {}
        for item in self.communities_dir.iterdir():
            if item.is_dir() and item.name not in self.whitelist:
                # Get folder stats
                size = self.get_folder_size(item)
                modified = datetime.fromtimestamp(item.stat().st_mtime)
                
                # Count content
                lessons = len(list((item / "lessons").glob("*.md"))) if (item / "lessons").exists() else 0
                videos = len(list((item / "videos").glob("*"))) if (item / "videos").exists() else 0
                images = len(list((item / "images").glob("*"))) if (item / "images").exists() else 0
                
                communities[item.name] = {
                    'path': item,
                    'size_mb': size / (1024 * 1024),
                    'modified': modified,
                    'lessons': lessons,
                    'videos': videos,
                    'images': images,
                    'total_files': lessons + videos + images
                }
        
        return communities
    
    def get_folder_size(self, folder_path):
        """Calculate total size of folder"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
        except:
            pass
        return total_size
    
    def display_communities(self, communities):
        """Display found communities with stats"""
        if not communities:
            print("📁 No community folders found to clean.")
            return
        
        print(f"\n📊 FOUND {len(communities)} COMMUNITY FOLDERS:")
        print("-" * 80)
        print(f"{'#':<3} {'Community Name':<35} {'Size':<10} {'Files':<8} {'Modified':<12}")
        print("-" * 80)
        
        for i, (name, info) in enumerate(communities.items(), 1):
            size_str = f"{info['size_mb']:.1f}MB"
            files_str = f"{info['total_files']}"
            modified_str = info['modified'].strftime("%Y-%m-%d")
            
            print(f"{i:<3} {name[:34]:<35} {size_str:<10} {files_str:<8} {modified_str:<12}")
        
        print("-" * 80)
        total_size = sum(info['size_mb'] for info in communities.values())
        total_files = sum(info['total_files'] for info in communities.values())
        print(f"{'TOTAL':<3} {'':<35} {total_size:.1f}MB{'':<2} {total_files:<8}")
        print()
    
    def create_backup(self, communities_to_backup, backup_name=None):
        """Create backup of specified communities"""
        if not communities_to_backup:
            return None
        
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / f"{backup_name}.zip"
        self.backup_dir.mkdir(exist_ok=True)
        
        print(f"💾 Creating backup: {backup_path.name}")
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for community_name in communities_to_backup:
                    community_path = self.communities_dir / community_name
                    if community_path.exists():
                        print(f"   📦 Backing up: {community_name}")
                        for file_path in community_path.rglob('*'):
                            if file_path.is_file():
                                arcname = file_path.relative_to(self.communities_dir)
                                zipf.write(file_path, arcname)
            
            print(f"✅ Backup created successfully: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def clean_communities(self, communities_to_clean, create_backup_first=True):
        """Clean specified communities"""
        if not communities_to_clean:
            print("📁 No communities selected for cleaning.")
            return
        
        # Create backup if requested
        backup_path = None
        if create_backup_first:
            backup_path = self.create_backup(communities_to_clean)
            if not backup_path:
                print("❌ Backup failed. Aborting cleanup for safety.")
                return
        
        # Perform cleanup
        print(f"\n🧹 CLEANING {len(communities_to_clean)} COMMUNITIES:")
        cleaned_count = 0
        
        for community_name in communities_to_clean:
            community_path = self.communities_dir / community_name
            if community_path.exists():
                try:
                    print(f"   🗑️  Removing: {community_name}")
                    shutil.rmtree(community_path)
                    cleaned_count += 1
                except Exception as e:
                    print(f"   ❌ Failed to remove {community_name}: {e}")
        
        print(f"\n✅ CLEANUP COMPLETE!")
        print(f"   📊 Cleaned: {cleaned_count}/{len(communities_to_clean)} communities")
        if backup_path:
            print(f"   💾 Backup: {backup_path.name}")
    
    def interactive_cleanup(self):
        """Interactive cleanup mode"""
        self.print_header()
        
        communities = self.scan_communities()
        if not communities:
            print("📁 No community folders found to clean.")
            return
        
        self.display_communities(communities)
        
        print("🎯 CLEANUP OPTIONS:")
        print("1. Clean ALL communities (with backup)")
        print("2. Clean specific communities")
        print("3. Clean by date (older than X days)")
        print("4. Clean by size (largest first)")
        print("5. View backups")
        print("6. Restore from backup")
        print("0. Exit")
        
        while True:
            try:
                choice = input("\n👉 Select option (0-6): ").strip()
                
                if choice == '0':
                    print("👋 Cleanup cancelled.")
                    return
                    
                elif choice == '1':
                    self.clean_all_communities(communities)
                    break
                    
                elif choice == '2':
                    self.clean_specific_communities(communities)
                    break
                    
                elif choice == '3':
                    self.clean_by_date(communities)
                    break
                    
                elif choice == '4':
                    self.clean_by_size(communities)
                    break
                    
                elif choice == '5':
                    self.view_backups()
                    
                elif choice == '6':
                    self.restore_from_backup()
                    
                else:
                    print("❌ Invalid option. Please select 0-6.")
                    
            except KeyboardInterrupt:
                print("\n👋 Cleanup cancelled.")
                return
    
    def clean_all_communities(self, communities):
        """Clean all communities with confirmation"""
        total_size = sum(info['size_mb'] for info in communities.values())
        total_files = sum(info['total_files'] for info in communities.values())
        
        print(f"\n⚠️  WARNING: This will delete ALL {len(communities)} community folders!")
        print(f"   📊 Total: {total_size:.1f}MB, {total_files} files")
        print("   💾 A backup will be created automatically.")
        
        confirm = input("\n❓ Are you sure? (type 'YES' to confirm): ").strip()
        if confirm == 'YES':
            self.clean_communities(list(communities.keys()), create_backup_first=True)
        else:
            print("👋 Cleanup cancelled.")
    
    def clean_specific_communities(self, communities):
        """Clean user-selected communities"""
        print("\n🎯 SELECT COMMUNITIES TO CLEAN:")
        print("Enter numbers separated by commas (e.g., 1,3,5) or 'all' for all:")
        
        community_list = list(communities.keys())
        
        selection = input("👉 Selection: ").strip().lower()
        
        if selection == 'all':
            selected = community_list
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected = [community_list[i] for i in indices if 0 <= i < len(community_list)]
            except:
                print("❌ Invalid selection format.")
                return
        
        if selected:
            selected_size = sum(communities[name]['size_mb'] for name in selected)
            selected_files = sum(communities[name]['total_files'] for name in selected)
            
            print(f"\n📋 SELECTED {len(selected)} COMMUNITIES:")
            for name in selected:
                print(f"   • {name}")
            print(f"   📊 Total: {selected_size:.1f}MB, {selected_files} files")
            
            confirm = input("\n❓ Proceed with cleanup? (y/N): ").strip().lower()
            if confirm == 'y':
                self.clean_communities(selected, create_backup_first=True)
            else:
                print("👋 Cleanup cancelled.")
        else:
            print("❌ No valid communities selected.")
    
    def clean_by_date(self, communities):
        """Clean communities older than specified days"""
        try:
            days = int(input("👉 Delete communities older than how many days? "))
            cutoff_date = datetime.now() - timedelta(days=days)
            
            old_communities = [
                name for name, info in communities.items()
                if info['modified'] < cutoff_date
            ]
            
            if old_communities:
                total_size = sum(communities[name]['size_mb'] for name in old_communities)
                print(f"\n📅 FOUND {len(old_communities)} communities older than {days} days:")
                for name in old_communities:
                    print(f"   • {name} (modified: {communities[name]['modified'].strftime('%Y-%m-%d')})")
                print(f"   📊 Total: {total_size:.1f}MB")
                
                confirm = input("\n❓ Proceed with cleanup? (y/N): ").strip().lower()
                if confirm == 'y':
                    self.clean_communities(old_communities, create_backup_first=True)
                else:
                    print("👋 Cleanup cancelled.")
            else:
                print(f"📅 No communities older than {days} days found.")
                
        except ValueError:
            print("❌ Invalid number of days.")
    
    def clean_by_size(self, communities):
        """Clean largest communities first"""
        try:
            count = int(input("👉 How many largest communities to clean? "))
            
            sorted_communities = sorted(
                communities.items(),
                key=lambda x: x[1]['size_mb'],
                reverse=True
            )
            
            largest = [name for name, _ in sorted_communities[:count]]
            
            if largest:
                total_size = sum(communities[name]['size_mb'] for name in largest)
                print(f"\n📊 LARGEST {len(largest)} COMMUNITIES:")
                for name in largest:
                    print(f"   • {name} ({communities[name]['size_mb']:.1f}MB)")
                print(f"   📊 Total: {total_size:.1f}MB")
                
                confirm = input("\n❓ Proceed with cleanup? (y/N): ").strip().lower()
                if confirm == 'y':
                    self.clean_communities(largest, create_backup_first=True)
                else:
                    print("👋 Cleanup cancelled.")
            else:
                print("❌ No communities to clean.")
                
        except ValueError:
            print("❌ Invalid number.")
    
    def view_backups(self):
        """View available backups"""
        if not self.backup_dir.exists():
            print("📦 No backups found.")
            return
        
        backups = list(self.backup_dir.glob("*.zip"))
        if not backups:
            print("📦 No backups found.")
            return
        
        print(f"\n📦 AVAILABLE BACKUPS ({len(backups)}):")
        print("-" * 60)
        
        for i, backup in enumerate(sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True), 1):
            size_mb = backup.stat().st_size / (1024 * 1024)
            modified = datetime.fromtimestamp(backup.stat().st_mtime)
            print(f"{i}. {backup.name} ({size_mb:.1f}MB, {modified.strftime('%Y-%m-%d %H:%M')})")
    
    def restore_from_backup(self):
        """Restore communities from backup"""
        if not self.backup_dir.exists():
            print("📦 No backups found.")
            return
        
        backups = list(self.backup_dir.glob("*.zip"))
        if not backups:
            print("📦 No backups found.")
            return
        
        self.view_backups()
        
        try:
            choice = int(input("\n👉 Select backup to restore (number): ")) - 1
            if 0 <= choice < len(backups):
                backup_path = sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True)[choice]
                
                print(f"\n⚠️  WARNING: This will restore from {backup_path.name}")
                print("   Any existing communities with the same names will be overwritten!")
                
                confirm = input("\n❓ Proceed with restore? (type 'YES' to confirm): ").strip()
                if confirm == 'YES':
                    self.restore_backup(backup_path)
                else:
                    print("👋 Restore cancelled.")
            else:
                print("❌ Invalid backup selection.")
        except ValueError:
            print("❌ Invalid selection.")
    
    def restore_backup(self, backup_path):
        """Restore from specific backup file"""
        try:
            print(f"📦 Restoring from: {backup_path.name}")
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(self.communities_dir)
            
            print("✅ Restore completed successfully!")
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Skool Scraper Cleanup Tool")
    parser.add_argument('--auto-clean', action='store_true', help='Auto-clean all communities')
    parser.add_argument('--days', type=int, help='Clean communities older than X days')
    parser.add_argument('--community', help='Clean specific community by name')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')
    
    args = parser.parse_args()
    
    cleaner = SkoolScraperCleaner()
    
    if args.auto_clean:
        communities = cleaner.scan_communities()
        if communities:
            cleaner.clean_communities(list(communities.keys()), not args.no_backup)
        else:
            print("📁 No communities found to clean.")
    elif args.days:
        communities = cleaner.scan_communities()
        cutoff_date = datetime.now() - timedelta(days=args.days)
        old_communities = [
            name for name, info in communities.items()
            if info['modified'] < cutoff_date
        ]
        if old_communities:
            cleaner.clean_communities(old_communities, not args.no_backup)
        else:
            print(f"📅 No communities older than {args.days} days found.")
    elif args.community:
        communities = cleaner.scan_communities()
        if args.community in communities:
            cleaner.clean_communities([args.community], not args.no_backup)
        else:
            print(f"❌ Community '{args.community}' not found.")
    else:
        cleaner.interactive_cleanup()

if __name__ == "__main__":
    main()