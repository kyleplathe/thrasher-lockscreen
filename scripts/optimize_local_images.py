#!/usr/bin/env python3
"""
Optimize Local Thrasher Cover Images
Optimizes downloaded images for iPhone lock screen display
"""

from PIL import Image
import os
import glob
from pathlib import Path

class LocalImageOptimizer:
    def __init__(self):
        self.lock_screen_size = (1080, 1920)  # iPhone lock screen ratio
        self.quality = 85  # JPEG quality
        self.max_file_size = 500 * 1024  # 500KB target
        
        # Directories
        self.input_dir = Path("../images/original")
        self.output_dir = Path("../images/optimized")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def optimize_image(self, input_path, output_path):
        """Optimize a single image for lock screen"""
        try:
            # Open image
            with Image.open(input_path) as image:
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Calculate aspect ratio
                img_ratio = image.width / image.height
                target_ratio = self.lock_screen_size[0] / self.lock_screen_size[1]
                
                # Resize image to fit lock screen
                if img_ratio > target_ratio:
                    # Image is wider than target - crop width
                    new_width = int(image.height * target_ratio)
                    left = (image.width - new_width) // 2
                    image = image.crop((left, 0, left + new_width, image.height))
                else:
                    # Image is taller than target - crop height
                    new_height = int(image.width / target_ratio)
                    top = (image.height - new_height) // 2
                    image = image.crop((0, top, image.width, top + new_height))
                
                # Resize to target dimensions
                image = image.resize(self.lock_screen_size, Image.Resampling.LANCZOS)
                
                # Save optimized image
                for quality in [self.quality, 80, 75, 70, 65]:
                    image.save(output_path, 'JPEG', quality=quality, optimize=True)
                    
                    # Check file size
                    file_size = os.path.getsize(output_path)
                    if file_size <= self.max_file_size:
                        return file_size, quality
                    elif quality <= 65:
                        # Keep the best we can do
                        return file_size, quality
                
                return os.path.getsize(output_path), self.quality
                
        except Exception as e:
            print(f"❌ Error optimizing {input_path.name}: {e}")
            return None, None
    
    def process_all_images(self):
        """Process all images in the input directory"""
        # Get all JPEG files
        image_files = list(self.input_dir.glob("*.jpg")) + list(self.input_dir.glob("*.jpeg"))
        
        print(f"📥 Found {len(image_files)} images to optimize")
        print(f"📁 Input: {self.input_dir}")
        print(f"📁 Output: {self.output_dir}")
        print(f"📏 Target size: {self.lock_screen_size[0]}x{self.lock_screen_size[1]}")
        print(f"💾 Target file size: {self.max_file_size/1024:.0f}KB")
        print()
        
        successful = 0
        failed = 0
        total_original_size = 0
        total_optimized_size = 0
        
        for i, input_path in enumerate(image_files, 1):
            # Create output filename
            output_filename = f"lock_screen_{input_path.stem}.jpg"
            output_path = self.output_dir / output_filename
            
            # Skip if already exists
            if output_path.exists():
                print(f"⏭️  Skipping {output_filename} (already exists)")
                successful += 1
                continue
            
            # Get original file size
            original_size = os.path.getsize(input_path)
            total_original_size += original_size
            
            # Optimize image
            optimized_size, quality = self.optimize_image(input_path, output_path)
            
            if optimized_size:
                total_optimized_size += optimized_size
                compression_ratio = (1 - optimized_size / original_size) * 100
                print(f"✅ {i:3d}/{len(image_files)}: {output_filename}")
                print(f"   📏 {original_size/1024:6.0f}KB → {optimized_size/1024:6.0f}KB ({compression_ratio:4.1f}% smaller)")
                print(f"   🎨 Quality: {quality}%")
                successful += 1
            else:
                print(f"❌ {i:3d}/{len(image_files)}: Failed to optimize {input_path.name}")
                failed += 1
            
            # Progress update
            if i % 10 == 0:
                print(f"📊 Progress: {i}/{len(image_files)} ({i/len(image_files)*100:.1f}%)")
        
        # Summary
        print(f"\n🎉 Optimization Complete!")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Optimized images saved to: {self.output_dir}")
        
        if total_original_size > 0:
            total_compression = (1 - total_optimized_size / total_original_size) * 100
            print(f"💾 Total size reduction: {total_original_size/1024/1024:.1f}MB → {total_optimized_size/1024/1024:.1f}MB ({total_compression:.1f}% smaller)")

def main():
    optimizer = LocalImageOptimizer()
    optimizer.process_all_images()

if __name__ == "__main__":
    main() 