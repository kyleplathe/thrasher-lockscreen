#!/usr/bin/env python3
"""
Create Fixed Text Overlay Script
Adds text overlays to the fixed centering images for iPhone 14 Pro Max
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class FixedTextOverlayProcessor:
    def __init__(self):
        self.input_dir = "images/optimized_final_fixed"
        self.output_dir = "images/fixed_text_overlay"
        # iPhone 14 Pro Max lock screen dimensions
        self.lock_screen_size = (1179, 2556)
        self.quality = 85
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Text positioning for iPhone 14 Pro Max
        self.text_x = 590  # Center horizontally (1179/2)
        self.text_y = 2200  # Position above bottom buttons
        self.text_color = (255, 255, 255)  # White
        self.text_bg_color = (0, 0, 0)  # Black background
        
        # Month names for display
        self.month_names = {
            "01": "January", "02": "February", "03": "March", "04": "April",
            "05": "May", "06": "June", "07": "July", "08": "August",
            "09": "September", "10": "October", "11": "November", "12": "December"
        }
        
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
                        font = ImageFont.truetype(path, 56)  # Larger font for iPhone 14 Pro Max
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
            padding = 25
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
    
    def extract_date_from_filename(self, filename):
        """Extract date information from filename"""
        try:
            # Remove file extension
            name = os.path.splitext(filename)[0]
            
            # Parse YYYY_MM format
            if '_' in name:
                parts = name.split('_')
                if len(parts) >= 2:
                    year = parts[0]
                    month_num = parts[1]
                    
                    # Get month name
                    month_name = self.month_names.get(month_num, month_num)
                    
                    return {
                        "year": year,
                        "month": month_name,
                        "month_num": month_num
                    }
            
            return None
            
        except Exception as e:
            print(f"Error extracting date from {filename}: {e}")
            return None
    
    def process_image_with_text(self, input_path, filename):
        """Process image and add text overlay"""
        try:
            # Open image
            image = Image.open(input_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract date information
            date_info = self.extract_date_from_filename(filename)
            
            if date_info:
                # Create text overlay
                text = f"{date_info['year']} - {date_info['month']}"
                
                # Add text overlay
                final_image = self.add_text_overlay(image, text)
                
                # Save image
                output_path = os.path.join(self.output_dir, filename)
                final_image.save(output_path, 'JPEG', quality=self.quality, optimize=True)
                
                return output_path, date_info
            else:
                print(f"Could not extract date from {filename}")
                return None, None
            
        except Exception as e:
            print(f"Error processing image {filename}: {e}")
            return None, None
    
    def create_text_overlay_collection(self):
        """Create the complete text overlay collection with fixed centering"""
        print("Creating text overlay collection with fixed centering...")
        
        if not os.path.exists(self.input_dir):
            print(f"Input directory {self.input_dir} not found!")
            return
        
        # Get all image files
        image_files = []
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(filename)
        
        print(f"Found {len(image_files)} images to process")
        
        processed_count = 0
        shortcuts_data = []
        
        for i, filename in enumerate(image_files):
            input_path = os.path.join(self.input_dir, filename)
            
            print(f"Processing {i+1}/{len(image_files)}: {filename}")
            
            # Process image with text overlay
            output_path, date_info = self.process_image_with_text(input_path, filename)
            
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
                    "file_size_mb": round(file_size_mb, 2),
                    "year": date_info.get("year", ""),
                    "month": date_info.get("month", ""),
                    "month_num": date_info.get("month_num", "")
                })
                
                print(f"✓ Created: {output_path}")
            else:
                print(f"✗ Failed to process: {filename}")
        
        # Save shortcuts JSON
        shortcuts_file = "shortcuts_fixed_text_overlay_covers.json"
        with open(shortcuts_file, 'w') as f:
            json.dump(shortcuts_data, f, indent=2)
        
        print(f"\nCompleted! Created {processed_count} images with text overlays.")
        print(f"Output directory: {self.output_dir}")
        print(f"Shortcuts JSON: {shortcuts_file}")
        
        return processed_count

def main():
    processor = FixedTextOverlayProcessor()
    processor.create_text_overlay_collection()

if __name__ == "__main__":
    main() 