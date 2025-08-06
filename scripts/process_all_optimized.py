#!/usr/bin/env python3
"""
Process All Optimized Images Script
Applies the new fitting method to all images in images/optimized/
"""

import os
from PIL import Image
import json

class AllOptimizedImageProcessor:
    def __init__(self):
        self.input_dir = "optimized_images"
        self.output_dir = "images/optimized_new"
        self.lock_screen_size = (1080, 1920)  # iPhone lock screen ratio
        self.quality = 85  # JPEG quality
        self.max_file_size = 500 * 1024  # 500KB target
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def process_image(self, input_path, output_filename):
        """Process image to fit full cover with borders"""
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
            
            # Save the processed image
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Try different quality settings to meet file size target
            for quality in [self.quality, 80, 75, 70, 65]:
                lock_screen_image.save(output_path, 'JPEG', quality=quality, optimize=True)
                
                # Check file size
                file_size = os.path.getsize(output_path)
                if file_size <= self.max_file_size:
                    print(f"✓ Processed {output_filename} ({file_size/1024:.1f}KB, quality: {quality})")
                    break
                elif quality <= 65:
                    print(f"⚠ Could not meet size target for {output_filename} ({file_size/1024:.1f}KB)")
                    break
            
            return output_path
            
        except Exception as e:
            print(f"Error processing {output_filename}: {e}")
            return None
    
    def process_all_images(self):
        """Process all images in the optimized directory"""
        print(f"Processing all images from {self.input_dir}...")
        
        if not os.path.exists(self.input_dir):
            print(f"Input directory {self.input_dir} not found!")
            return 0, 0
        
        processed_count = 0
        failed_count = 0
        
        # Get all image files
        image_files = []
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(filename)
        
        print(f"Found {len(image_files)} images to process")
        
        for i, filename in enumerate(image_files):
            input_path = os.path.join(self.input_dir, filename)
            
            print(f"Processing {i+1}/{len(image_files)}: {filename}")
            
            # Process image
            result = self.process_image(input_path, filename)
            if result:
                processed_count += 1
            else:
                failed_count += 1
        
        print(f"\nProcessing complete!")
        print(f"Successfully processed: {processed_count}")
        print(f"Failed: {failed_count}")
        print(f"Output directory: {self.output_dir}")
        
        return processed_count, failed_count
    
    def create_shortcuts_ready_json(self):
        """Create JSON file ready for iOS Shortcuts"""
        shortcuts_data = []
        
        # Scan output directory
        for filename in os.listdir(self.output_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(self.output_dir, filename)
                file_size = os.path.getsize(file_path)
                
                shortcuts_data.append({
                    'filename': filename,
                    'local_path': file_path,
                    'file_size': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2)
                })
        
        # Save shortcuts-ready JSON
        shortcuts_file = 'shortcuts_all_optimized_covers.json'
        with open(shortcuts_file, 'w') as f:
            json.dump(shortcuts_data, f, indent=2)
        
        print(f"Created shortcuts-ready JSON: {shortcuts_file}")
        print(f"Contains {len(shortcuts_data)} optimized covers")
        
        return shortcuts_file

def main():
    processor = AllOptimizedImageProcessor()
    
    print("Thrasher All Optimized Image Processor")
    print("=" * 45)
    print("This will process all images from images/optimized/ with the new fitting method")
    
    # Process all images
    processed, failed = processor.process_all_images()
    
    # Create shortcuts-ready JSON
    shortcuts_file = processor.create_shortcuts_ready_json()
    
    print(f"\nSummary:")
    print(f"✓ Processed {processed} images")
    print(f"✓ Created {shortcuts_file} for iOS Shortcuts")
    print(f"\nNext steps:")
    print(f"1. Review the processed images in '{processor.output_dir}'")
    print(f"2. If satisfied, you can replace the old optimized images")
    print(f"3. Use '{shortcuts_file}' in your iOS Shortcut")

if __name__ == "__main__":
    main() 