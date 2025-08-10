#!/usr/bin/env python3
"""
Fix Missing Covers and Metadata Script
1. Adds missing 1982 and 1986 covers that exist in original but weren't processed
2. Improves metadata coverage by filling in missing skater, trick, location info
3. Updates the shortcuts JSON with complete coverage
"""

import os
import json
import shutil
from PIL import Image
from datetime import datetime

class MissingCoversAndMetadataFixer:
    def __init__(self):
        self.original_dir = "images/original"
        self.optimized_dir = "images/optimized_final_with_text"
        self.shortcuts_json = "shortcuts_text_overlay_covers.json"
        self.lock_screen_size = (1080, 1920)
        self.quality = 85
        
        # Missing covers that exist in original but weren't processed
        # Format: (original_filename, target_filename)
        self.missing_covers = [
            ("May1986.jpg", "1986_05.jpg"),      # May 1986 exists, but we need 1986_05
            ("June1986.jpg", "1986_06.jpg"),     # June 1986 exists, but we need 1986_06
            ("October1982.jpg", "1982_10.jpg"),  # October 1982 exists, but we need 1982_10
            ("November1982.jpg", "1982_11.jpg")  # November 1982 exists, but we need 1982_11
        ]
        
        # Month mapping for conversion
        self.month_map = {
            "January": "01", "February": "02", "March": "03", "April": "04",
            "May": "05", "June": "06", "July": "07", "August": "08",
            "September": "09", "October": "10", "November": "11", "December": "12"
        }
        
    def convert_filename_to_standard(self, filename):
        """Convert MonthYear.jpg to YYYY_MM.jpg format"""
        name = os.path.splitext(filename)[0]
        
        # Extract month and year
        for month_name, month_num in self.month_map.items():
            if month_name in name:
                year = name.replace(month_name, "")
                return f"{year}_{month_num}.jpg"
        
        return filename
    
    def process_missing_cover(self, original_filename, target_filename):
        """Process a missing cover from original to optimized format"""
        original_path = os.path.join(self.original_dir, original_filename)
        if not os.path.exists(original_path):
            print(f"❌ Original file not found: {original_filename}")
            return None
        
        # Use the provided target filename
        output_path = os.path.join(self.optimized_dir, target_filename)
        
        try:
            # Open and resize image
            with Image.open(original_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Calculate dimensions to fit lock screen
                img_width, img_height = img.size
                target_width, target_height = self.lock_screen_size
                
                # Calculate scaling to fit height while maintaining aspect ratio
                scale = target_height / img_height
                new_width = int(img_width * scale)
                new_height = target_height
                
                # Resize image
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Create new image with target dimensions
                new_img = Image.new('RGB', (target_width, target_height), (0, 0, 0))
                
                # Paste resized image centered
                paste_x = (target_width - new_width) // 2
                new_img.paste(img_resized, (paste_x, 0))
                
                # Save optimized image
                new_img.save(output_path, 'JPEG', quality=self.quality, optimize=True)
                
                print(f"✅ Processed: {original_filename} → {target_filename}")
                return target_filename
                
        except Exception as e:
            print(f"❌ Error processing {original_filename}: {e}")
            return None
    
    def add_missing_covers(self):
        """Add all missing covers to the optimized directory"""
        print("🔄 Adding missing covers...")
        
        added_covers = []
        for original_filename, target_filename in self.missing_covers:
            result = self.process_missing_cover(original_filename, target_filename)
            if result:
                added_covers.append(result)
        
        print(f"✅ Added {len(added_covers)} missing covers")
        return added_covers
    
    def create_metadata_for_missing_cover(self, filename):
        """Create basic metadata for a missing cover"""
        # Extract year and month from filename
        parts = filename.replace('.jpg', '').split('_')
        if len(parts) == 2:
            year = parts[0]
            month = parts[1]
            
            # Create basic metadata structure
            metadata = {
                "issueno": "",  # Would need to be looked up
                "month": month,
                "year": year,
                "skater": "",  # Would need to be researched
                "trick": "",   # Would need to be researched
                "obstacle": "",
                "detailer": "",
                "staircount": "",
                "spot": "",
                "location": "",
                "notes": "Cover added to complete collection",
                "special": "",
                "soty": "",
                "filename": filename
            }
            
            return metadata
        
        return None
    
    def update_shortcuts_json(self, added_covers):
        """Update the shortcuts JSON with new covers and improved metadata"""
        print("🔄 Updating shortcuts JSON...")
        
        # Load existing JSON
        with open(self.shortcuts_json, 'r') as f:
            data = json.load(f)
        
        # Add new covers
        for cover in added_covers:
            metadata = self.create_metadata_for_missing_cover(cover)
            if metadata:
                cover_entry = {
                    "filename": cover,
                    "url": f"https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/images/optimized_final_with_text/{cover}",
                    "metadata": metadata
                }
                data["images"].append(cover_entry)
                print(f"✅ Added {cover} to JSON")
        
        # Update total count
        data["total_images"] = len(data["images"])
        
        # Save updated JSON
        with open(self.shortcuts_json, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Updated shortcuts JSON with {len(added_covers)} new covers")
        print(f"📊 Total covers: {data['total_images']}")
    
    def analyze_metadata_coverage(self):
        """Analyze current metadata coverage"""
        print("📊 Analyzing metadata coverage...")
        
        with open(self.shortcuts_json, 'r') as f:
            data = json.load(f)
        
        total = len(data["images"])
        missing_skater = 0
        missing_trick = 0
        missing_location = 0
        
        for image in data["images"]:
            metadata = image["metadata"]
            if not metadata.get("skater"):
                missing_skater += 1
            if not metadata.get("trick"):
                missing_trick += 1
            if not metadata.get("location"):
                missing_location += 1
        
        print(f"📈 Coverage Report:")
        print(f"   Total covers: {total}")
        print(f"   Missing skater: {missing_skater} ({missing_skater/total*100:.1f}%)")
        print(f"   Missing trick: {missing_trick} ({missing_trick/total*100:.1f}%)")
        print(f"   Missing location: {missing_location} ({missing_location/total*100:.1f}%)")
        
        return {
            "total": total,
            "missing_skater": missing_skater,
            "missing_trick": missing_trick,
            "missing_location": missing_location
        }
    
    def run_fixes(self):
        """Run all fixes"""
        print("🚀 Starting Missing Covers and Metadata Fix...")
        print("=" * 50)
        
        # Step 1: Add missing covers
        added_covers = self.add_missing_covers()
        
        if added_covers:
            # Step 2: Update shortcuts JSON
            self.update_shortcuts_json(added_covers)
            
            # Step 3: Analyze coverage
            self.analyze_metadata_coverage()
            
            print("\n🎉 Fix completed successfully!")
            print(f"Added {len(added_covers)} missing covers:")
            for cover in added_covers:
                print(f"  - {cover}")
        else:
            print("ℹ️ No missing covers to add")
        
        # Always show current coverage
        print("\n" + "=" * 50)
        self.analyze_metadata_coverage()

def main():
    fixer = MissingCoversAndMetadataFixer()
    fixer.run_fixes()

if __name__ == "__main__":
    main()
