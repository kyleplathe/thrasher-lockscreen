#!/usr/bin/env python3
"""
GitHub Integration with Text Overlay Script
Pulls images from GitHub repository and adds text overlays with 4ply metadata
"""

import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64

class GitHubImageProcessor:
    def __init__(self):
        self.github_api_base = "https://api.github.com/repos/kyleplathe/thrasher-lockscreen/contents"
        self.output_dir = "images/github_text_overlay"
        self.lock_screen_size = (1080, 1920)
        self.quality = 85
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Text positioning
        self.text_x = 540  # Center horizontally
        self.text_y = 1700  # Position above bottom buttons
        self.text_color = (255, 255, 255)  # White
        self.text_bg_color = (0, 0, 0)  # Black background
        
    def get_github_file_content(self, file_path):
        """Get file content from GitHub"""
        try:
            url = f"{self.github_api_base}/{file_path}"
            response = requests.get(url)
            response.raise_for_status()
            
            content_data = response.json()
            if 'content' in content_data:
                # Decode base64 content
                content = base64.b64decode(content_data['content'])
                return content
            else:
                print(f"No content found for {file_path}")
                return None
                
        except Exception as e:
            print(f"Error fetching {file_path}: {e}")
            return None
    
    def get_github_directory_listing(self, directory_path):
        """Get directory listing from GitHub"""
        try:
            url = f"{self.github_api_base}/{directory_path}"
            response = requests.get(url)
            response.raise_for_status()
            
            files = response.json()
            return [file['name'] for file in files if file['type'] == 'file']
            
        except Exception as e:
            print(f"Error fetching directory listing for {directory_path}: {e}")
            return []
    
    def add_text_overlay(self, image, text):
        """Add text overlay to image"""
        try:
            img_with_text = image.copy()
            draw = ImageDraw.Draw(img_with_text)
            
            # Try to load font
            try:
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
                new_width = self.lock_screen_size[0]
                new_height = int(new_width / img_ratio)
            else:
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
    
    def create_test_images_from_github(self):
        """Create test images by pulling from GitHub"""
        print("Creating test images from GitHub with text overlays...")
        
        # Test cover information
        test_covers = [
            {
                "filename": "1981_01.jpg",
                "github_path": "images/optimized_final/1981_01.jpg",
                "year": "1981",
                "month": "January",
                "title": "Thrasher Magazine"
            },
            {
                "filename": "1990_06.jpg",
                "github_path": "images/optimized_final/1990_06.jpg", 
                "year": "1990",
                "month": "June",
                "title": "Skateboarding"
            },
            {
                "filename": "2000_12.jpg",
                "github_path": "images/optimized_final/2000_12.jpg",
                "year": "2000", 
                "month": "December",
                "title": "Thrasher"
            },
            {
                "filename": "2010_03.jpg",
                "github_path": "images/optimized_final/2010_03.jpg",
                "year": "2010",
                "month": "March", 
                "title": "Skateboarding"
            },
            {
                "filename": "2020_08.jpg",
                "github_path": "images/optimized_final/2020_08.jpg",
                "year": "2020",
                "month": "August",
                "title": "Thrasher Magazine"
            }
        ]
        
        processed_count = 0
        
        for cover_info in test_covers:
            filename = cover_info["filename"]
            github_path = cover_info["github_path"]
            
            print(f"Processing {filename} from GitHub...")
            
            # Get image from GitHub
            image_data = self.get_github_file_content(github_path)
            
            if image_data:
                # Process image with text overlay
                output_path = self.process_image_with_text(image_data, filename, cover_info)
                
                if output_path:
                    processed_count += 1
                    print(f"✓ Created: {output_path}")
                else:
                    print(f"✗ Failed to process: {filename}")
            else:
                print(f"✗ Failed to download: {filename}")
        
        print(f"\nCompleted! Created {processed_count} test images from GitHub with text overlays.")
        print(f"Output directory: {self.output_dir}")
        
        return processed_count

def main():
    processor = GitHubImageProcessor()
    processor.create_test_images_from_github()

if __name__ == "__main__":
    main() 