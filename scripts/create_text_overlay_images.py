#!/usr/bin/env python3
"""
Create Text Overlay Images Script
Adds text overlays to lock screen images with cover details
Positioned between flashlight and camera buttons
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

class TextOverlayImageProcessor:
    def __init__(self):
        self.output_dir = "images/text_overlay_test"
        self.lock_screen_size = (1080, 1920)  # iPhone lock screen ratio
        self.quality = 85  # JPEG quality
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Text positioning (between flashlight and camera buttons)
        # iPhone lock screen: flashlight at ~25% from left, camera at ~75% from left
        # Center text at 50% horizontally, position vertically in bottom area
        self.text_x = 540  # Center horizontally (1080/2)
        self.text_y = 1700  # Position above bottom buttons
        self.text_color = (255, 255, 255)  # White
        self.text_bg_color = (0, 0, 0)  # Black background
        
    def download_image(self, url):
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BytesIO(response.content)
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None
    
    def add_text_overlay(self, image, text):
        """Add text overlay to image"""
        try:
            # Create a copy of the image
            img_with_text = image.copy()
            draw = ImageDraw.Draw(img_with_text)
            
            # Try to load Roboto font, fallback to default if not available
            try:
                # Try different font paths
                font_paths = [
                    "/System/Library/Fonts/Helvetica.ttc",  # macOS
                    "/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf",  # Linux
                    "C:/Windows/Fonts/arial.ttf",  # Windows
                ]
                
                font = None
                for path in font_paths:
                    if os.path.exists(path):
                        font = ImageFont.truetype(path, 48)
                        break
                
                if font is None:
                    # Fallback to default font
                    font = ImageFont.load_default()
                    
            except Exception:
                font = ImageFont.load_default()
            
            # Get text dimensions
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate background rectangle
            padding = 20
            bg_x1 = self.text_x - text_width // 2 - padding
            bg_y1 = self.text_y - text_height // 2 - padding
            bg_x2 = self.text_x + text_width // 2 + padding
            bg_y2 = self.text_y + text_height // 2 + padding
            
            # Draw background rectangle
            draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=self.text_bg_color)
            
            # Draw text
            draw.text((self.text_x, self.text_y), text, font=font, fill=self.text_color, anchor="mm")
            
            return img_with_text
            
        except Exception as e:
            print(f"Error adding text overlay: {e}")
            return image
    
    def process_image_with_text(self, image_data, filename, cover_info):
        """Process image and add text overlay"""
        try:
            # Open image
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create black background with lock screen dimensions
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
            
            # Resize image
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Calculate position to center image
            x = (self.lock_screen_size[0] - new_width) // 2
            y = (self.lock_screen_size[1] - new_height) // 2
            
            # Paste image onto background
            background.paste(image, (x, y))
            
            # Create text overlay
            text = f"{cover_info['year']} - {cover_info['month']}"
            if 'title' in cover_info and cover_info['title']:
                text += f"\n{cover_info['title']}"
            
            # Add text overlay
            final_image = self.add_text_overlay(background, text)
            
            # Save image
            output_path = os.path.join(self.output_dir, filename)
            final_image.save(output_path, 'JPEG', quality=self.quality, optimize=True)
            
            return output_path
            
        except Exception as e:
            print(f"Error processing image {filename}: {e}")
            return None
    
    def create_test_images(self):
        """Create 5 test images with text overlays"""
        print("Creating 5 test images with text overlays...")
        
        # Sample cover information for testing
        test_covers = [
            {
                "filename": "1981_01.jpg",
                "year": "1981",
                "month": "January",
                "title": "Thrasher Magazine"
            },
            {
                "filename": "1990_06.jpg", 
                "year": "1990",
                "month": "June",
                "title": "Skateboarding"
            },
            {
                "filename": "2000_12.jpg",
                "year": "2000", 
                "month": "December",
                "title": "Thrasher"
            },
            {
                "filename": "2010_03.jpg",
                "year": "2010",
                "month": "March", 
                "title": "Skateboarding"
            },
            {
                "filename": "2020_08.jpg",
                "year": "2020",
                "month": "August",
                "title": "Thrasher Magazine"
            }
        ]
        
        processed_count = 0
        
        for cover_info in test_covers:
            filename = cover_info["filename"]
            input_path = f"images/optimized_final/{filename}"
            
            if os.path.exists(input_path):
                print(f"Processing {filename}...")
                
                # Read image data
                with open(input_path, 'rb') as f:
                    image_data = f.read()
                
                # Process image with text overlay
                output_path = self.process_image_with_text(image_data, filename, cover_info)
                
                if output_path:
                    processed_count += 1
                    print(f"✓ Created: {output_path}")
                else:
                    print(f"✗ Failed to process: {filename}")
            else:
                print(f"✗ File not found: {input_path}")
        
        print(f"\nCompleted! Created {processed_count} test images with text overlays.")
        print(f"Output directory: {self.output_dir}")
        
        return processed_count

def main():
    processor = TextOverlayImageProcessor()
    processor.create_test_images()

if __name__ == "__main__":
    main() 