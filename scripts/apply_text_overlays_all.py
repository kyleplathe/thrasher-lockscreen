#!/usr/bin/env python3
"""
Apply Text Overlays to All Images Script
Applies text overlays to all 550 images using 4ply CSV data
Uses the final perfected layout with bold dates and centered text
"""

import csv
import os
from PIL import Image, ImageDraw, ImageFont
import json

class TextOverlayApplier:
    def __init__(self):
        self.input_dir = "images/original"
        self.output_dir = "images/optimized_final_with_text"
        self.csv_file = "data/4ply_covers.csv"
        self.lock_screen_size = (1179, 2556)  # iPhone 14 Pro Max
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load 4ply data
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
        
        print(f"Loaded {len(fourply_data)} entries from 4ply CSV")
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
    
    def load_fonts(self):
        """Load fonts with fallback - try to get bold for date"""
        try:
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
            ]
            
            for path in font_paths:
                if os.path.exists(path):
                    # Try to load bold if possible
                    try:
                        font_large_bold = ImageFont.truetype(path, size=56, index=1)  # Index 1 = Bold
                    except:
                        font_large_bold = ImageFont.truetype(path, 56)
                    font_large = ImageFont.truetype(path, 56)
                    font_medium = ImageFont.truetype(path, 48)
                    return {
                        "large_bold": font_large_bold,
                        "large": font_large,
                        "medium": font_medium
                    }
        except Exception:
            pass
        default = ImageFont.load_default()
        return {"large_bold": default, "large": default, "medium": default}
    
    def get_month_name(self, month_num):
        """Convert month number to name"""
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        return months[month_num - 1] if 1 <= month_num <= 12 else ''

    def get_month_label(self, month_value):
        """Return display month label for numeric and special issues."""
        if month_value is None:
            return ''
        month_raw = str(month_value).strip()
        if not month_raw:
            return ''
        special_labels = {
            "photoissue": "Photo Issue",
            "photo issue": "Photo Issue",
            "summer": "Summer",
            "special issue": "Special Issue",
            "winter": "Winter",
        }
        month_key = month_raw.lower()
        if month_key in special_labels:
            return special_labels[month_key]
        try:
            return self.get_month_name(int(month_raw))
        except Exception:
            return ''

    def is_redundant_year_line(self, text, year):
        """Skip extra standalone year lines that duplicate the date."""
        return str(text).strip() == str(year).strip()
    
    def create_text_overlay(self, image_path, metadata):
        """Create text overlay using finalized layout"""
        try:
            # Open and format image
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create lock screen with black background
            lock_screen_image = Image.new('RGB', self.lock_screen_size, (0, 0, 0))
            img_ratio = image.width / image.height
            target_ratio = self.lock_screen_size[0] / self.lock_screen_size[1]
            
            if img_ratio > target_ratio:
                scale_factor = self.lock_screen_size[0] / image.width
                new_width = self.lock_screen_size[0]
                new_height = int(image.height * scale_factor)
            else:
                scale_factor = self.lock_screen_size[1] / image.height
                new_width = int(image.width * scale_factor)
                new_height = self.lock_screen_size[1]
            
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            x_offset = (self.lock_screen_size[0] - new_width) // 2
            y_offset = (self.lock_screen_size[1] - new_height) // 2
            lock_screen_image.paste(resized_image, (x_offset, y_offset))
            
            overlay_image = lock_screen_image
            draw = ImageDraw.Draw(overlay_image)
            fonts = self.load_fonts()
            
            # Colors
            text_color = (255, 255, 255)
            outline_color = (0, 0, 0)
            outline_width = 3
            text_x = 590  # Center horizontally
            
            # FIXED POSITIONING - Date at fixed position
            date_y = 2228
            
            # Build date line (BOLD)
            month_name = self.get_month_label(metadata.get('month', ''))
            date_text = f"{month_name} {metadata.get('year', '')}"
            date_font = fonts["large_bold"]  # Bold font
            date_bbox = draw.textbbox((0, 0), date_text, font=date_font)
            date_height = date_bbox[3] - date_bbox[1]
            
            # Draw date with outline
            date_y_centered = date_y + (date_height // 2)
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((text_x + dx, date_y_centered + dy), date_text, font=date_font, 
                                 fill=outline_color, anchor="mm")
            draw.text((text_x, date_y_centered), date_text, font=date_font, fill=text_color, anchor="mm")
            
            # Badge gap
            badge_gap = 80
            after_badge_y = date_y + date_height + badge_gap
            
            # Build lines BELOW badge
            below_lines = []
            skater = (metadata.get('skater') or '').strip()
            if skater and not self.is_redundant_year_line(skater, metadata.get('year', '')):
                below_lines.append((skater, fonts["large"]))
            if metadata.get('trick') and metadata['trick'].strip():
                below_lines.append((metadata['trick'].strip(), fonts["medium"]))
            if metadata.get('location') and metadata['location'].strip():
                below_lines.append((metadata['location'].strip(), fonts["medium"]))
            
            # Tight spacing for all lines (using 4-line format as base)
            tight_spacing = 20  # Tight spacing
            
            # Calculate total height of all lines below badge
            total_height = 0
            for text, font in below_lines:
                bbox = draw.textbbox((0, 0), text, font=font)
                total_height += (bbox[3] - bbox[1])
            if len(below_lines) > 1:
                total_height += (len(below_lines) - 1) * tight_spacing
            
            # Center the entire block in available space below badge
            bottom_limit = 2520  # Home swipe
            available_space = bottom_limit - after_badge_y
            start_y_below = after_badge_y + ((available_space - total_height) // 2)
            
            # Draw lines BELOW badge with tight spacing
            current_draw_y = start_y_below
            for text, font in below_lines:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_height = bbox[3] - bbox[1]
                text_y = current_draw_y + (text_height // 2)
                
                # Draw outline
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((text_x + dx, text_y + dy), text, font=font, 
                                     fill=outline_color, anchor="mm")
                
                # Draw main text
                draw.text((text_x, text_y), text, font=font, fill=text_color, anchor="mm")
                
                current_draw_y += text_height + tight_spacing
            
            # Save the image
            filename = os.path.basename(image_path)
            output_path = os.path.join(self.output_dir, filename)
            overlay_image.save(output_path, quality=95)
            
            return output_path
            
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return None
    
    def process_all_images(self):
        """Process all images to add text overlays"""
        print("🚀 Applying text overlays to all images...")
        print("   Using finalized layout: bold dates, centered text below badge")
        print()
        
        if not os.path.exists(self.input_dir):
            print(f"❌ Input directory {self.input_dir} not found!")
            return
        
        # Get all image files
        image_files = []
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(filename)
        
        print(f"📁 Found {len(image_files)} images to process")
        print()
        
        processed_count = 0
        failed_count = 0
        processed_files = []
        
        for i, filename in enumerate(image_files):
            if (i + 1) % 50 == 0:
                print(f"Processing {i+1}/{len(image_files)}: {filename}...")
            
            image_path = os.path.join(self.input_dir, filename)
            
            # Extract date from filename
            name_without_ext = os.path.splitext(filename)[0]
            if '_' in name_without_ext:
                parts = name_without_ext.split('_')
                if len(parts) >= 2:
                    year = parts[0]
                    month = parts[1]
                    
                    # Look up metadata in 4ply data
                    key = f"{year}_{month}"
                    metadata = self.fourply_data.get(key, {})
                    
                    # Add date info from filename
                    metadata['year'] = year
                    metadata['month'] = month
                    
                    # Create text overlay
                    output_path = self.create_text_overlay(image_path, metadata)
                    if output_path:
                        processed_count += 1
                        processed_files.append({
                            'input': filename,
                            'output': os.path.basename(output_path),
                            'metadata': metadata
                        })
                    else:
                        failed_count += 1
        
        # Save processing info
        processing_info = {
            'total_images': len(image_files),
            'processed_count': processed_count,
            'failed_count': failed_count,
            'processed_files': processed_files
        }
        
        with open('text_overlay_processing_info.json', 'w') as f:
            json.dump(processing_info, f, indent=2)
        
        print()
        print("✅ Processing complete!")
        print(f"   Successfully processed: {processed_count}")
        print(f"   Failed: {failed_count}")
        print(f"   Output directory: {self.output_dir}")
        print(f"   Processing info: text_overlay_processing_info.json")
        
        return processing_info

def main():
    applier = TextOverlayApplier()
    info = applier.process_all_images()
    
    print()
    print("🎨 Text overlays applied to all images!")

if __name__ == "__main__":
    main()
