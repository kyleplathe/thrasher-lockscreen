#!/usr/bin/env/python3
"""
Compare Text Positions Script
Creates side-by-side comparisons of old vs new text positioning
"""

import csv
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json

class TextPositionComparer:
    def __init__(self):
        self.input_dir = "images/optimized_final_fixed"
        self.old_output_dir = "images/old_position_test"
        self.new_output_dir = "images/test_improved_alignment"
        self.comparison_dir = "images/text_position_comparison"
        self.csv_file = "data/4ply_covers.csv"
        self.config_file = "text_overlay_config.json"
        self.lock_screen_size = (1179, 2556)  # iPhone 14 Pro Max
        
        # Create directories
        os.makedirs(self.old_output_dir, exist_ok=True)
        os.makedirs(self.comparison_dir, exist_ok=True)
        
        # Load configuration
        self.config = self.load_config()
        
        # Load 4ply data
        self.fourply_data = self.load_4ply_data()
        
        # Old positioning (what you had before)
        self.old_text_y = 2210
        
        # New positioning (improved)
        self.bottom_widgets_start = 2400
        self.text_area_height = 200
        self.new_text_y_center = 2350  # Moved down for better spacing above bottom widgets
        
        # Test images to compare
        self.test_images = [
            "1981_01.jpg",  # Single line
            "1990_06.jpg",  # Multiple lines
            "2000_12.jpg",  # Multiple lines
        ]
        
    def load_config(self):
        """Load configuration file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            print(f"Configuration file {self.config_file} not found!")
            return None
    
    def load_4ply_data(self):
        """Load 4ply CSV data into a dictionary"""
        fourply_data = {}
        
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    year = row['year']
                    month = self.month_to_number(row['month'])
                    if month:
                        key = f"{year}_{month:02d}"
                        fourply_data[key] = row
            
            print(f"Loaded {len(fourply_data)} entries from 4ply CSV")
        else:
            print(f"4ply CSV file {self.csv_file} not found!")
        
        return fourply_data
    
    def month_to_number(self, month_name):
        """Convert month name to number"""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'winter': 12
        }
        return months.get(month_name.lower())
    
    def create_old_position_overlay(self, image_path, metadata):
        """Create text overlay with old positioning"""
        try:
            image = Image.open(image_path)
            overlay_image = image.copy()
            draw = ImageDraw.Draw(overlay_image)
            
            # Load fonts
            font_config = self.config["font_settings"]
            try:
                font_large = ImageFont.truetype(f"{font_config['font_family']}-Bold.ttf", font_config["large_size"])
                font_medium = ImageFont.truetype(f"{font_config['font_family']}-Regular.ttf", font_config["medium_size"])
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
            
            # Get colors and positioning
            text_color = tuple(self.config["colors"]["text_color"])
            outline_color = tuple(self.config["colors"]["outline_color"])
            outline_width = self.config["colors"]["outline_width"]
            text_x = self.config["positioning"]["text_x"]
            line_spacing = self.config["positioning"]["line_spacing"]
            
            # Build text content
            lines = []
            content_config = self.config["content"]
            
            if content_config["show_date"] and metadata.get('year') and metadata.get('month'):
                month_name = self.get_month_name(int(metadata['month']))
                date_text = f"{month_name} {metadata['year']}"
                lines.append(("date", date_text))
            
            if content_config["show_skater"] and metadata.get('skater') and metadata['skater'].strip():
                skater_text = metadata['skater'].strip()
                lines.append(("skater", skater_text))
            
            if content_config["show_trick"] and metadata.get('trick') and metadata['trick'].strip():
                trick_text = metadata['trick'].strip()
                lines.append(("trick", trick_text))
            
            if content_config["show_location"] and metadata.get('location') and metadata['location'].strip():
                location_text = metadata['location'].strip()
                lines.append(("location", location_text))
            
            # Draw text with old positioning (fixed Y position)
            current_y = self.old_text_y
            for i, (line_type, line) in enumerate(lines):
                if line_type in ["date", "skater"]:
                    font = font_large
                else:
                    font = font_medium
                
                # Get text bounds
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Center horizontally
                x = text_x - (text_width // 2)
                y = current_y - (text_height // 2)
                
                # Draw outline and text
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        draw.text((x + dx, y + dy), line, font=font, fill=outline_color)
                draw.text((x, y), line, font=font, fill=text_color)
                
                current_y += text_height + line_spacing
            
            # Save old position version
            filename = os.path.basename(image_path)
            output_path = os.path.join(self.old_output_dir, filename)
            overlay_image.save(output_path, quality=95)
            
            return output_path
            
        except Exception as e:
            print(f"Error creating old position overlay: {e}")
            return None
    
    def get_month_name(self, month_num):
        """Convert month number to name"""
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return months[month_num - 1] if 1 <= month_num <= 12 else ''
    
    def create_comparison_image(self, old_path, new_path, filename):
        """Create side-by-side comparison image"""
        try:
            # Open both images
            old_img = Image.open(old_path)
            new_img = Image.open(new_path)
            
            # Ensure both images are the same size
            if old_img.size != new_img.size:
                new_img = new_img.resize(old_img.size, Image.Resampling.LANCZOS)
            
            # Create comparison image (side by side)
            width, height = old_img.size
            comparison = Image.new('RGB', (width * 2, height))
            
            # Paste images side by side
            comparison.paste(old_img, (0, 0))
            comparison.paste(new_img, (width, 0))
            
            # Add labels
            draw = ImageDraw.Draw(comparison)
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
            except:
                font = ImageFont.load_default()
            
            # Add labels at the top
            draw.text((width//2 - 100, 50), "OLD POSITION", font=font, fill=(255, 0, 0))
            draw.text((width + width//2 - 100, 50), "NEW POSITION", font=font, fill=(0, 255, 0))
            
            # Add positioning info
            info_font = ImageFont.load_default()
            old_info = f"Y: {self.old_text_y}"
            new_info = f"Y: {self.new_text_y_center}"
            
            draw.text((50, height - 100), old_info, font=info_font, fill=(255, 255, 255))
            draw.text((width + 50, height - 100), new_info, font=info_font, fill=(255, 255, 255))
            
            # Save comparison
            output_path = os.path.join(self.comparison_dir, f"comparison_{filename}")
            comparison.save(output_path, quality=95)
            
            return output_path
            
        except Exception as e:
            print(f"Error creating comparison image: {e}")
            return None
    
    def create_comparisons(self):
        """Create comparisons between old and new text positioning"""
        print("🔄 Creating text position comparisons...")
        print(f"📱 Old position: Y = {self.old_text_y}")
        print(f"🎯 New position: Y = {self.new_text_y_center}")
        print(f"📍 Bottom widgets start at: Y = {self.bottom_widgets_start}")
        print()
        
        if not os.path.exists(self.input_dir):
            print(f"❌ Input directory {self.input_dir} not found!")
            return
        
        if not os.path.exists(self.new_output_dir):
            print(f"❌ New position directory {self.new_output_dir} not found!")
            print("Run test_improved_alignment.py first!")
            return
        
        comparison_count = 0
        
        for filename in self.test_images:
            input_path = os.path.join(self.input_dir, filename)
            
            if os.path.exists(input_path):
                print(f"🔄 Processing: {filename}")
                
                # Extract metadata
                name_without_ext = os.path.splitext(filename)[0]
                if '_' in name_without_ext:
                    parts = name_without_ext.split('_')
                    if len(parts) >= 2:
                        year = parts[0]
                        month = parts[1]
                        
                        # Look up metadata
                        key = f"{year}_{month}"
                        metadata = self.fourply_data.get(key, {})
                        metadata['year'] = year
                        metadata['month'] = month
                        
                        # Create old position version
                        old_path = self.create_old_position_overlay(input_path, metadata)
                        
                        # Check if new version exists
                        new_path = os.path.join(self.new_output_dir, filename)
                        
                        if old_path and os.path.exists(new_path):
                            # Create comparison
                            comparison_path = self.create_comparison_image(old_path, new_path, filename)
                            if comparison_path:
                                comparison_count += 1
                                print(f"  ✅ Created comparison: {os.path.basename(comparison_path)}")
                            else:
                                print(f"  ❌ Failed to create comparison")
                        else:
                            print(f"  ⚠️  Missing old or new version")
                else:
                    print(f"  ⚠️  Could not parse filename format")
            else:
                print(f"  ⚠️  File not found: {input_path}")
            
            print()
        
        print(f"🎯 Comparison complete!")
        print(f"✅ Created {comparison_count} comparison images")
        print(f"📁 Comparison directory: {self.comparison_dir}")
        print()
        print("🔍 Check the comparison images to see the difference!")
        print("📝 The new positioning should look much better centered between the bottom widgets.")

def main():
    comparer = TextPositionComparer()
    comparer.create_comparisons()

if __name__ == "__main__":
    main()
