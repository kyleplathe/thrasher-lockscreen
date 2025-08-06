#!/usr/bin/env python3
"""
Fix Centering Issues Script
Fixes centering issues for iPhone 14 Pro Max lock screen images
"""

import os
from PIL import Image
import json

class CenteringFixProcessor:
    def __init__(self):
        self.input_dir = "images/optimized_final"
        self.output_dir = "images/optimized_final_fixed"
        # iPhone 14 Pro Max lock screen dimensions (actual display area)
        self.lock_screen_size = (1179, 2556)  # Updated for iPhone 14 Pro Max
        self.quality = 85
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
    def fix_image_centering(self, input_path, filename):
        """Fix image centering for iPhone 14 Pro Max"""
        try:
            # Open image
            image = Image.open(input_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create black background with iPhone 14 Pro Max dimensions
            background = Image.new('RGB', self.lock_screen_size, (0, 0, 0))
            
            # Calculate scaling to fit image within lock screen
            img_ratio = image.width / image.height
            target_ratio = self.lock_screen_size[0] / self.lock_screen_size[1]
            
            if img_ratio > target_ratio:
                # Image is wider - scale to fit width
                new_width = self.lock_screen_size[0]
                new_height = int(new_width / img_ratio)
            else:
                # Image is taller - scale to fit height
                new_height = self.lock_screen_size[1]
                new_width = int(new_height * img_ratio)
            
            # Resize image with high quality
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Calculate position to center image perfectly
            x = (self.lock_screen_size[0] - new_width) // 2
            y = (self.lock_screen_size[1] - new_height) // 2
            
            # Paste image onto background
            background.paste(image, (x, y))
            
            # Save image
            output_path = os.path.join(self.output_dir, filename)
            background.save(output_path, 'JPEG', quality=self.quality, optimize=True)
            
            return output_path
            
        except Exception as e:
            print(f"Error processing image {filename}: {e}")
            return None
    
    def process_all_images(self):
        """Process all images to fix centering"""
        print("Fixing centering for all optimized_final images...")
        
        if not os.path.exists(self.input_dir):
            print(f"Input directory {self.input_dir} not found!")
            return
        
        # Get all image files
        image_files = []
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(filename)
        
        print(f"Found {len(image_files)} images to fix")
        
        processed_count = 0
        shortcuts_data = []
        
        for i, filename in enumerate(image_files):
            input_path = os.path.join(self.input_dir, filename)
            
            print(f"Processing {i+1}/{len(image_files)}: {filename}")
            
            # Fix image centering
            output_path = self.fix_image_centering(input_path, filename)
            
            if output_path:
                processed_count += 1
                
                # Get file size
                file_size = os.path.getsize(output_path)
                file_size_mb = file_size / (1024 * 1024)
                
                # Add to shortcuts data
                shortcuts_data.append({
                    "filename": filename,
                    "local_path": output_path,
                    "file_size": file_size,
                    "file_size_mb": round(file_size_mb, 2)
                })
                
                print(f"✓ Fixed: {output_path}")
            else:
                print(f"✗ Failed to process: {filename}")
        
        # Save shortcuts JSON
        shortcuts_file = "shortcuts_fixed_centering_covers.json"
        with open(shortcuts_file, 'w') as f:
            json.dump(shortcuts_data, f, indent=2)
        
        print(f"\nCompleted! Fixed centering for {processed_count} images.")
        print(f"Output directory: {self.output_dir}")
        print(f"Shortcuts JSON: {shortcuts_file}")
        
        return processed_count

def main():
    processor = CenteringFixProcessor()
    processor.process_all_images()

if __name__ == "__main__":
    main() 