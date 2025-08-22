#!/usr/bin/env/python3
"""
Test Improved Text Overlay Alignment Script
Processes a few sample images to demonstrate the improved positioning
"""

import csv
import os
from PIL import Image, ImageDraw, ImageFont
import json

class TestImprovedTextOverlay:
    def __init__(self):
        self.input_dir = "images/optimized_final_fixed"
        self.output_dir = "images/test_improved_alignment"
        self.csv_file = "data/4ply_covers.csv"
        self.config_file = "text_overlay_config.json"
        self.lock_screen_size = (1179, 2556)  # iPhone 14 Pro Max
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load configuration
        self.config = self.load_config()
        
        # Load 4ply data
        self.fourply_data = self.load_4ply_data()
        
        # iPhone 14 Pro Max bottom widget positioning
        self.bottom_widgets_start = 2400
        self.text_area_height = 200
        self.text_y_center = 2350  # Moved down for better spacing above bottom widgets
        
        # Test images to process
        self.test_images = [
            "1981_01.jpg",  # Single line (just date)
            "1990_06.jpg",  # Multiple lines
            "2000_12.jpg",  # Multiple lines
            "2010_03.jpg",  # Multiple lines
            "2020_08.jpg"   # Multiple lines
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
    
    def calculate_optimal_text_position(self, lines, fonts):
        """Calculate optimal text position for perfect centering"""
        if not lines:
            return self.text_y_center, 0
        
        # Calculate total height needed for all text
        total_height = 0
        
        for i, (line_type, line) in enumerate(lines):
            if line_type in ["date", "skater"]:
                font = fonts["large"]
            else:
                font = fonts["medium"]
            
            # Get text bounds
            temp_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
            bbox = temp_draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]
            total_height += line_height
        
        # Add spacing between lines
        if len(lines) > 1:
            total_height += (len(lines) - 1) * self.config["positioning"]["line_spacing"]
        
        # Calculate starting position to center the entire text block
        start_y = self.text_y_center - (total_height // 2)
        
        return start_y, total_height
    
    def create_text_overlay(self, image_path, metadata):
        """Create perfectly aligned text overlay on image"""
        try:
            # Open image
            image = Image.open(image_path)
            
            # Create a copy for drawing
            overlay_image = image.copy()
            draw = ImageDraw.Draw(overlay_image)
            
            # Load fonts based on configuration
            font_config = self.config["font_settings"]
            try:
                font_large = ImageFont.truetype(f"{font_config['font_family']}-Bold.ttf", font_config["large_size"])
                font_medium = ImageFont.truetype(f"{font_config['font_family']}-Regular.ttf", font_config["medium_size"])
            except:
                # Fallback fonts
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
            
            fonts = {
                "large": font_large,
                "medium": font_medium
            }
            
            # Get colors from config
            text_color = tuple(self.config["colors"]["text_color"])
            outline_color = tuple(self.config["colors"]["outline_color"])
            outline_width = self.config["colors"]["outline_width"]
            
            # Get positioning from config
            pos_config = self.config["positioning"]
            text_x = pos_config["text_x"]
            line_spacing = pos_config["line_spacing"]
            
            # Build text content based on config
            lines = []
            content_config = self.config["content"]
            
            # Date line
            if content_config["show_date"] and metadata.get('year') and metadata.get('month'):
                month_name = self.get_month_name(int(metadata['month']))
                date_text = f"{month_name} {metadata['year']}"
                lines.append(("date", date_text))
            
            # Skater line
            if content_config["show_skater"] and metadata.get('skater') and metadata['skater'].strip():
                skater_text = metadata['skater'].strip()
                lines.append(("skater", skater_text))
            
            # Trick line
            if content_config["show_trick"] and metadata.get('trick') and metadata['trick'].strip():
                trick_text = metadata['trick'].strip()
                lines.append(("trick", trick_text))
            
            # Location line
            if content_config["show_location"] and metadata.get('location') and metadata['location'].strip():
                location_text = metadata['location'].strip()
                lines.append(("location", location_text))
            
            # Calculate optimal starting position for perfect centering
            start_y, total_height = self.calculate_optimal_text_position(lines, fonts)
            
            print(f"  Text lines: {len(lines)}")
            print(f"  Total height: {total_height}px")
            print(f"  Starting Y: {start_y}")
            print(f"  Text center: {self.text_y_center}")
            
            # Draw text lines with perfect centering
            current_y = start_y
            for i, (line_type, line) in enumerate(lines):
                # Choose font based on line type
                if line_type in ["date", "skater"]:
                    font = fonts["large"]
                else:
                    font = fonts["medium"]
                
                # Get text bounds for horizontal centering
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Center the text horizontally
                x = text_x - (text_width // 2)
                
                # Position text vertically (center of current line)
                y = current_y - (text_height // 2)
                
                # Draw outline for better visibility
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        draw.text((x + dx, y + dy), line, font=font, fill=outline_color)
                
                # Draw main text
                draw.text((x, y), line, font=font, fill=text_color)
                
                # Move to next line position
                current_y += text_height + line_spacing
            
            # Save the image
            filename = os.path.basename(image_path)
            output_path = os.path.join(self.output_dir, filename)
            overlay_image.save(output_path, quality=95)
            
            return output_path
            
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return None
    
    def get_month_name(self, month_num):
        """Convert month number to name"""
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return months[month_num - 1] if 1 <= month_num <= 12 else ''
    
    def test_improved_alignment(self):
        """Test improved text overlay alignment on sample images"""
        print("🧪 Testing improved text overlay alignment...")
        print(f"📱 iPhone 14 Pro Max dimensions: {self.lock_screen_size[0]}x{self.lock_screen_size[1]}")
        print(f"🎯 Text will be centered at y={self.text_y_center}")
        print(f"📍 Bottom widgets start around y={self.bottom_widgets_start}")
        print(f"📏 Text area height: {self.text_area_height}px")
        print()
        
        if not os.path.exists(self.input_dir):
            print(f"❌ Input directory {self.input_dir} not found!")
            return
        
        processed_count = 0
        failed_count = 0
        
        for filename in self.test_images:
            input_path = os.path.join(self.input_dir, filename)
            
            if os.path.exists(input_path):
                print(f"🔄 Processing: {filename}")
                
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
                        
                        # Create improved text overlay
                        output_path = self.create_text_overlay(input_path, metadata)
                        if output_path:
                            processed_count += 1
                            print(f"  ✅ Created: {os.path.basename(output_path)}")
                        else:
                            failed_count += 1
                            print(f"  ❌ Failed to process")
                else:
                    print(f"  ⚠️  Could not parse filename format")
            else:
                print(f"  ⚠️  File not found: {input_path}")
            
            print()
        
        print(f"🎯 Test complete!")
        print(f"✅ Successfully processed: {processed_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📁 Output directory: {self.output_dir}")
        print()
        print("🔍 Check the test images to see the improved alignment!")
        print("📝 The text should now be perfectly centered between the bottom widgets.")

def main():
    tester = TestImprovedTextOverlay()
    tester.test_improved_alignment()

if __name__ == "__main__":
    main()
