#!/usr/bin/env python3
"""
Thrasher Cover Image Optimizer
Optimizes images for iPhone lock screen display
"""

import requests
from PIL import Image, ImageDraw, ImageFont
import json
import os
import time
from urllib.parse import urlparse
import io

class ThrasherImageOptimizer:
    def __init__(self):
        self.lock_screen_size = (1080, 1920)  # iPhone lock screen ratio
        self.quality = 85  # JPEG quality
        self.max_file_size = 500 * 1024  # 500KB target
        self.output_dir = "optimized_images"
        self.font_path = None  # Will be set if available
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
    def download_image(self, url, timeout=10):
        """Download image from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return None
    
    def optimize_image(self, image_data, filename, metadata=None):
        """Optimize image for lock screen with full cover visible"""
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
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
            
            # Use the lock screen image for further processing
            image = lock_screen_image
            
            # Add metadata overlay if provided
            if metadata:
                image = self.add_metadata_overlay(image, metadata)
            
            # Save optimized image
            output_path = os.path.join(self.output_dir, filename)
            
            # Try different quality settings to meet file size target
            for quality in [self.quality, 80, 75, 70, 65]:
                image.save(output_path, 'JPEG', quality=quality, optimize=True)
                
                # Check file size
                file_size = os.path.getsize(output_path)
                if file_size <= self.max_file_size:
                    print(f"✓ Optimized {filename} ({file_size/1024:.1f}KB, quality: {quality})")
                    break
                elif quality <= 65:
                    print(f"⚠ Could not meet size target for {filename} ({file_size/1024:.1f}KB)")
                    break
            
            return output_path
            
        except Exception as e:
            print(f"Error optimizing {filename}: {e}")
            return None
    
    def add_metadata_overlay(self, image, metadata):
        """Add metadata text overlay to image"""
        try:
            # Create a copy of the image
            overlay_image = image.copy()
            draw = ImageDraw.Draw(overlay_image)
            
            # Try to load a font
            font_size = 40
            try:
                # Try system fonts
                font_paths = [
                    "/System/Library/Fonts/Helvetica.ttc",
                    "/System/Library/Fonts/Arial.ttf",
                    "/Library/Fonts/Arial.ttf"
                ]
                
                font = None
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, font_size)
                        break
                
                if not font:
                    font = ImageFont.load_default()
                    
            except Exception:
                font = ImageFont.load_default()
            
            # Prepare text content
            text_lines = []
            
            # Add date
            if metadata.get('date'):
                text_lines.append(f"📅 {metadata['date']}")
            
            # Add skaters
            if metadata.get('skaters'):
                skaters_text = ", ".join(metadata['skaters'][:2])  # Limit to 2 skaters
                text_lines.append(f"👤 {skaters_text}")
            
            # Add tricks
            if metadata.get('tricks'):
                tricks_text = ", ".join(metadata['tricks'][:2])  # Limit to 2 tricks
                text_lines.append(f"🛹 {tricks_text}")
            
            # Add obstacles
            if metadata.get('obstacles'):
                obstacles_text = ", ".join(metadata['obstacles'][:1])  # Limit to 1 obstacle
                text_lines.append(f"🏗️ {obstacles_text}")
            
            # Add location
            if metadata.get('location'):
                text_lines.append(f"📍 {metadata['location']}")
            
            # Draw text overlay
            y_position = 50
            for line in text_lines:
                # Create semi-transparent background for text
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Background rectangle
                bg_rect = [
                    30, y_position - 5,
                    30 + text_width + 20, y_position + text_height + 5
                ]
                
                # Semi-transparent background
                bg_color = (0, 0, 0, 128)  # Black with 50% opacity
                bg_image = Image.new('RGBA', overlay_image.size, (0, 0, 0, 0))
                bg_draw = ImageDraw.Draw(bg_image)
                bg_draw.rectangle(bg_rect, fill=bg_color)
                
                # Composite background onto image
                overlay_image = Image.alpha_composite(overlay_image.convert('RGBA'), bg_image)
                draw = ImageDraw.Draw(overlay_image)
                
                # Draw text
                draw.text((40, y_position), line, fill=(255, 255, 255), font=font)
                y_position += text_height + 15
            
            return overlay_image.convert('RGB')
            
        except Exception as e:
            print(f"Error adding metadata overlay: {e}")
            return image
    
    def process_covers_batch(self, covers_file, metadata_file=None, limit=None):
        """Process a batch of covers"""
        print(f"Processing covers from {covers_file}...")
        
        # Load covers
        with open(covers_file, 'r') as f:
            covers = json.load(f)
        
        # Load metadata if available
        metadata_dict = {}
        if metadata_file and os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata_data = json.load(f)
                for cover in metadata_data:
                    if 'url' in cover:
                        metadata_dict[cover['url']] = cover.get('metadata', {})
        
        # Limit processing if specified
        if limit:
            covers = covers[:limit]
        
        processed_count = 0
        failed_count = 0
        
        for i, cover in enumerate(covers):
            # Handle different cover formats
            if isinstance(cover, dict):
                url = cover.get('url', '')
                date = cover.get('date', '')
            else:
                url = cover
                date = ''
            
            if not url:
                continue
            
            # Extract filename from URL
            filename = os.path.basename(urlparse(url).path)
            if not filename or '.' not in filename:
                filename = f"cover_{i:04d}.jpg"
            
            # Get metadata for this cover
            metadata = metadata_dict.get(url, {})
            
            print(f"Processing {i+1}/{len(covers)}: {filename}")
            
            # Download image
            image_data = self.download_image(url)
            if not image_data:
                failed_count += 1
                continue
            
            # Optimize image
            result = self.optimize_image(image_data, filename, metadata)
            if result:
                processed_count += 1
            else:
                failed_count += 1
            
            # Be respectful with requests
            time.sleep(0.5)
        
        print(f"\nProcessing complete!")
        print(f"Successfully processed: {processed_count}")
        print(f"Failed: {failed_count}")
        print(f"Output directory: {self.output_dir}")
        
        return processed_count, failed_count
    
    def create_shortcuts_ready_json(self, optimized_dir=None):
        """Create JSON file ready for iOS Shortcuts"""
        if not optimized_dir:
            optimized_dir = self.output_dir
        
        shortcuts_data = []
        
        # Scan optimized directory
        for filename in os.listdir(optimized_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(optimized_dir, filename)
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
    optimizer = ThrasherImageOptimizer()
    
    # Process covers with metadata
    print("Thrasher Cover Image Optimizer")
    print("=" * 40)
    
    # Check if metadata file exists
    metadata_file = 'enhanced_covers_with_metadata.json'
    if not os.path.exists(metadata_file):
        metadata_file = None
        print("No metadata file found, processing without overlays")
    
    # Process a sample batch first
    processed, failed = optimizer.process_covers_batch(
        'data/shortcuts/final_comprehensive_verified_urls.json',
        metadata_file=metadata_file,
        limit=10  # Start with 10 covers for testing
    )
    
    # Create shortcuts-ready JSON
    shortcuts_file = optimizer.create_shortcuts_ready_json()
    
    print(f"\nNext steps:")
    print(f"1. Review the optimized images in '{optimizer.output_dir}'")
    print(f"2. If satisfied, remove the limit and process all covers")
    print(f"3. Use '{shortcuts_file}' in your iOS Shortcut")
    print(f"4. Upload the optimized images to GitHub for easy access")

if __name__ == "__main__":
    main() 