#!/usr/bin/env python3
"""
Create Text Overlay Shortcuts JSON Script
Generates a JSON file for iOS Shortcuts with all text overlay images
"""

import os
import json
import csv

class TextOverlayShortcutsCreator:
    def __init__(self):
        self.input_dir = "images/optimized_final_with_text"
        self.csv_file = "data/4ply_covers.csv"
        self.output_file = "shortcuts_text_overlay_covers.json"
        
        # Load 4ply data for metadata
        self.fourply_data = self.load_4ply_data()
        
    def load_4ply_data(self):
        """Load 4ply CSV data into a dictionary"""
        fourply_data = {}
        
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Create key in YYYY_MM format
                year = row['year']
                month = self.month_to_number(row['month'])
                if month:
                    key = f"{year}_{month:02d}"
                    fourply_data[key] = row
                
                # Also store by special issue type
                if row['month'].lower() in ['summer', 'winter']:
                    special_key = f"{year}_{row['month'].lower()}"
                    fourply_data[special_key] = row
        
        return fourply_data
    
    def month_to_number(self, month_name):
        """Convert month name to number"""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'winter': 12  # Winter issue typically December
        }
        return months.get(month_name.lower())
    
    def get_metadata_for_image(self, filename):
        """Get metadata for an image"""
        name_without_ext = os.path.splitext(filename)[0]
        
        if '_' in name_without_ext:
            parts = name_without_ext.split('_')
            if len(parts) >= 2:
                year = parts[0]
                month_or_special = parts[1]
                
                # Try to find metadata
                key = f"{year}_{month_or_special}"
                metadata = self.fourply_data.get(key, {})
                
                # Add basic info
                metadata['filename'] = filename
                metadata['year'] = year
                metadata['month'] = month_or_special
                
                return metadata
        
        return {'filename': filename}
    
    def create_shortcuts_json(self):
        """Create JSON file for iOS Shortcuts"""
        print("Creating text overlay shortcuts JSON...")
        
        if not os.path.exists(self.input_dir):
            print(f"Input directory {self.input_dir} not found!")
            return
        
        # Get all image files
        image_files = []
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(filename)
        
        print(f"Found {len(image_files)} images to process")
        
        # Create shortcuts data
        shortcuts_data = {
            "version": "1.0",
            "description": "Thrasher Magazine covers with text overlays for iOS Shortcuts",
            "total_images": len(image_files),
            "images": []
        }
        
        for i, filename in enumerate(image_files):
            print(f"Processing {i+1}/{len(image_files)}: {filename}")
            
            # Get metadata
            metadata = self.get_metadata_for_image(filename)
            
            # Create image entry
            image_entry = {
                "filename": filename,
                "url": f"https://raw.githubusercontent.com/kyleplathe/thrasher-lockscreen/main/images/optimized_final_with_text/{filename}",
                "metadata": metadata
            }
            
            shortcuts_data["images"].append(image_entry)
        
        # Save JSON file
        with open(self.output_file, 'w') as f:
            json.dump(shortcuts_data, f, indent=2)
        
        print(f"\n✅ Created shortcuts JSON: {self.output_file}")
        print(f"Total images: {len(image_files)}")
        
        return shortcuts_data

def main():
    creator = TextOverlayShortcutsCreator()
    data = creator.create_shortcuts_json()
    
    print("\n🎨 Text overlay shortcuts JSON created!")
    print("📱 Ready for iOS Shortcuts integration!")

if __name__ == "__main__":
    main()
