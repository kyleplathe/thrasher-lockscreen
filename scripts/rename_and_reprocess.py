#!/usr/bin/env python3
"""
Rename Original Images and Reprocess Optimized Images
1. Renames original images in chronological order with number format
2. Applies new fitting method to optimized_images
"""

import os
import re
from datetime import datetime
from PIL import Image
import json
import shutil

class ImageRenamerAndReprocessor:
    def __init__(self):
        self.original_dir = "images/original"
        self.optimized_dir = "optimized_images"
        self.renamed_original_dir = "images/original_renamed"
        self.lock_screen_size = (1080, 1920)  # iPhone lock screen ratio
        self.quality = 85  # JPEG quality
        self.max_file_size = 500 * 1024  # 500KB target
        
        # Create directories
        os.makedirs(self.renamed_original_dir, exist_ok=True)
    
    def extract_date_from_filename(self, filename):
        """Extract date from filename using various patterns"""
        # Remove file extension
        name = os.path.splitext(filename)[0]
        
        # Pattern 1: MonthYear (e.g., January1981, Feb1981)
        month_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\d{4})'
        match = re.search(month_pattern, name, re.IGNORECASE)
        if match:
            month, year = match.groups()
            return self.parse_month_year(month, year)
        
        # Pattern 2: YYYY_MM format (e.g., 2024_11)
        year_month_pattern = r'(\d{4})_(\d{1,2})'
        match = re.search(year_month_pattern, name)
        if match:
            year, month = match.groups()
            try:
                return datetime(int(year), int(month), 1)
            except ValueError:
                pass
        
        # Pattern 3: MM_YYYY format (e.g., 11_2024)
        month_year_pattern = r'(\d{1,2})_(\d{4})'
        match = re.search(month_year_pattern, name)
        if match:
            month, year = match.groups()
            try:
                return datetime(int(year), int(month), 1)
            except ValueError:
                pass
        
        # Pattern 4: CV1TH format (e.g., CV1TH0124 for Jan 2024)
        cv_pattern = r'CV1TH(\d{2})(\d{2})'
        match = re.search(cv_pattern, name)
        if match:
            month, year = match.groups()
            try:
                return datetime(2000 + int(year), int(month), 1)
            except ValueError:
                pass
        
        # Pattern 5: 25_XX format (e.g., 25_01 for Jan 2025)
        year25_pattern = r'25_(\d{2})'
        match = re.search(year25_pattern, name)
        if match:
            month = match.group(1)
            try:
                return datetime(2025, int(month), 1)
            except ValueError:
                pass
        
        # Pattern 6: 09_25 format (e.g., 09_25 for Sep 2025)
        month25_pattern = r'(\d{2})_25'
        match = re.search(month25_pattern, name)
        if match:
            month = match.group(1)
            try:
                return datetime(2025, int(month), 1)
            except ValueError:
                pass
        
        # Default to current date if no pattern matches
        return datetime.now()
    
    def parse_month_year(self, month_str, year_str):
        """Parse month and year strings to datetime"""
        month_map = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        
        month = month_map.get(month_str.lower(), 1)
        year = int(year_str)
        return datetime(year, month, 1)
    
    def rename_original_images(self):
        """Rename original images in chronological order"""
        print("Renaming original images in chronological order...")
        
        if not os.path.exists(self.original_dir):
            print(f"Original directory {self.original_dir} not found!")
            return
        
        # Get all image files
        image_files = []
        for filename in os.listdir(self.original_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(filename)
        
        print(f"Found {len(image_files)} original images")
        
        # Extract dates and sort
        dated_files = []
        for filename in image_files:
            date = self.extract_date_from_filename(filename)
            dated_files.append((date, filename))
        
        # Sort by date
        dated_files.sort(key=lambda x: x[0])
        
        # Rename files with number format
        renamed_count = 0
        for i, (date, filename) in enumerate(dated_files, 1):
            # Create new filename with number format
            extension = os.path.splitext(filename)[1]
            new_filename = f"{i:04d}_{date.strftime('%Y_%m')}{extension}"
            
            # Copy to renamed directory
            old_path = os.path.join(self.original_dir, filename)
            new_path = os.path.join(self.renamed_original_dir, new_filename)
            
            try:
                shutil.copy2(old_path, new_path)
                print(f"✓ {i:04d}: {filename} → {new_filename}")
                renamed_count += 1
            except Exception as e:
                print(f"✗ Error copying {filename}: {e}")
        
        print(f"\nRenamed {renamed_count} original images")
        print(f"Renamed images saved to: {self.renamed_original_dir}")
        
        return renamed_count
    
    def reprocess_optimized_images(self):
        """Reprocess optimized images with new fitting method"""
        print(f"\nReprocessing optimized images from {self.optimized_dir}...")
        
        if not os.path.exists(self.optimized_dir):
            print(f"Optimized directory {self.optimized_dir} not found!")
            return
        
        processed_count = 0
        failed_count = 0
        
        # Get all image files
        image_files = []
        for filename in os.listdir(self.optimized_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(filename)
        
        print(f"Found {len(image_files)} optimized images to reprocess")
        
        for i, filename in enumerate(image_files):
            input_path = os.path.join(self.optimized_dir, filename)
            
            print(f"Processing {i+1}/{len(image_files)}: {filename}")
            
            # Reprocess image
            result = self.reprocess_image(input_path, filename)
            if result:
                processed_count += 1
            else:
                failed_count += 1
        
        print(f"\nReprocessing complete!")
        print(f"Successfully processed: {processed_count}")
        print(f"Failed: {failed_count}")
        
        return processed_count, failed_count
    
    def reprocess_image(self, input_path, output_filename):
        """Reprocess image to fit full cover with borders"""
        try:
            # Open the existing optimized image
            image = Image.open(input_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create a new image with lock screen dimensions and black background
            lock_screen_image = Image.new('RGB', self.lock_screen_size, (0, 0, 0))
            
            # Calculate scaling to fit the entire magazine cover
            img_ratio = image.width / image.height
            target_ratio = self.lock_screen_size[0] / self.lock_screen_size[1]
            
            # Scale image to fit within lock screen while maintaining aspect ratio
            if img_ratio > target_ratio:
                # Image is wider than target - scale to fit width
                scale_factor = self.lock_screen_size[0] / image.width
                new_width = self.lock_screen_size[0]
                new_height = int(image.height * scale_factor)
            else:
                # Image is taller than target - scale to fit height
                scale_factor = self.lock_screen_size[1] / image.height
                new_width = int(image.width * scale_factor)
                new_height = self.lock_screen_size[1]
            
            # Resize the magazine cover
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Calculate position to center the image
            x_offset = (self.lock_screen_size[0] - new_width) // 2
            y_offset = (self.lock_screen_size[1] - new_height) // 2
            
            # Paste the resized magazine cover onto the lock screen background
            lock_screen_image.paste(resized_image, (x_offset, y_offset))
            
            # Save the reprocessed image (overwrite original)
            output_path = os.path.join(self.optimized_dir, output_filename)
            
            # Try different quality settings to meet file size target
            for quality in [self.quality, 80, 75, 70, 65]:
                lock_screen_image.save(output_path, 'JPEG', quality=quality, optimize=True)
                
                # Check file size
                file_size = os.path.getsize(output_path)
                if file_size <= self.max_file_size:
                    print(f"✓ Reprocessed {output_filename} ({file_size/1024:.1f}KB, quality: {quality})")
                    break
                elif quality <= 65:
                    print(f"⚠ Could not meet size target for {output_filename} ({file_size/1024:.1f}KB)")
                    break
            
            return output_path
            
        except Exception as e:
            print(f"Error reprocessing {output_filename}: {e}")
            return None
    
    def create_shortcuts_ready_json(self):
        """Create JSON file ready for iOS Shortcuts"""
        shortcuts_data = []
        
        # Scan optimized directory
        for filename in os.listdir(self.optimized_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(self.optimized_dir, filename)
                file_size = os.path.getsize(file_path)
                
                shortcuts_data.append({
                    'filename': filename,
                    'local_path': file_path,
                    'file_size': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2)
                })
        
        # Save shortcuts-ready JSON
        shortcuts_file = 'shortcuts_optimized_covers.json'
        with open(shortcuts_file, 'w') as f:
            json.dump(shortcuts_data, f, indent=2)
        
        print(f"Created shortcuts-ready JSON: {shortcuts_file}")
        print(f"Contains {len(shortcuts_data)} optimized covers")
        
        return shortcuts_file

def main():
    processor = ImageRenamerAndReprocessor()
    
    print("Thrasher Image Renamer and Reprocessor")
    print("=" * 50)
    
    # Step 1: Rename original images
    renamed_count = processor.rename_original_images()
    
    # Step 2: Reprocess optimized images
    processed, failed = processor.reprocess_optimized_images()
    
    # Step 3: Create shortcuts-ready JSON
    shortcuts_file = processor.create_shortcuts_ready_json()
    
    print(f"\nSummary:")
    print(f"✓ Renamed {renamed_count} original images")
    print(f"✓ Reprocessed {processed} optimized images")
    print(f"✓ Created {shortcuts_file} for iOS Shortcuts")
    print(f"\nNext steps:")
    print(f"1. Review the renamed original images in '{processor.renamed_original_dir}'")
    print(f"2. Review the reprocessed optimized images in '{processor.optimized_dir}'")
    print(f"3. Use '{shortcuts_file}' in your iOS Shortcut")

if __name__ == "__main__":
    main() 