#!/usr/bin/env python3
"""
Apply Text Overlays to All Images Script
Applies text overlays to all 550 images using 4ply CSV data
Includes configuration file for easy editing later
"""

import csv
import os
from PIL import Image, ImageDraw, ImageFont
import json

class TextOverlayApplier:
    def __init__(self):
        self.input_dir = "images/optimized_final_fixed"
        self.output_dir = "images/optimized_final_with_text"
        self.csv_file = "data/4ply_covers.csv"
        self.config_file = "text_overlay_config.json"
        self.lock_screen_size = (1179, 2556)  # iPhone 14 Pro Max
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load configuration
        self.config = self.load_config()
        
        # Load 4ply data
        self.fourply_data = self.load_4ply_data()
        
    def load_config(self):
        """Load or create configuration file"""
        default_config = {
            "font_settings": {
                "large_size": 56,
                "medium_size": 48,
                "small_size": 40,
                "font_family": "Roboto"
            },
            "positioning": {
                "text_x": 590,
                "text_y_start": 2200,
                "line_spacing": 70
            },
            "colors": {
                "text_color": [255, 255, 255],  # White
                "outline_color": [0, 0, 0],     # Black
                "outline_width": 3
            },
            "content": {
                "show_date": True,
                "show_skater": True,
                "show_trick": True,
                "show_location": True,
                "show_obstacle": False
            }
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults in case new options were added
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
        else:
            config = default_config
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        
        return config
    
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
    
    def create_text_overlay(self, image_path, metadata):
        """Create text overlay on image using configuration"""
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
                font_small = ImageFont.truetype(f"{font_config['font_family']}-Regular.ttf", font_config["small_size"])
            except:
                # Fallback fonts
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Get colors from config
            text_color = tuple(self.config["colors"]["text_color"])
            outline_color = tuple(self.config["colors"]["outline_color"])
            outline_width = self.config["colors"]["outline_width"]
            
            # Get positioning from config
            pos_config = self.config["positioning"]
            text_x = pos_config["text_x"]
            text_y_start = pos_config["text_y_start"]
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
            
            # Obstacle line (if enabled)
            if content_config["show_obstacle"] and metadata.get('obstacle') and metadata['obstacle'].strip():
                obstacle_text = metadata['obstacle'].strip()
                lines.append(("obstacle", obstacle_text))
            
            # Location line
            if content_config["show_location"] and metadata.get('location') and metadata['location'].strip():
                location_text = metadata['location'].strip()
                lines.append(("location", location_text))
            
            # Draw text lines
            for i, (line_type, line) in enumerate(lines):
                # Choose font based on line type
                if line_type in ["date", "skater"]:
                    font = font_large
                else:
                    font = font_medium
                
                # Calculate text position
                text_y = text_y_start + (i * line_spacing)
                
                # Get text bounds for centering
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Center the text
                x = text_x - (text_width // 2)
                y = text_y - (text_height // 2)
                
                # Draw outline
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        draw.text((x + dx, y + dy), line, font=font, fill=outline_color)
                
                # Draw main text
                draw.text((x, y), line, font=font, fill=text_color)
            
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
    
    def process_all_images(self):
        """Process all images to add text overlays"""
        print("Applying text overlays to all images...")
        
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
        failed_count = 0
        processed_files = []
        
        for i, filename in enumerate(image_files):
            print(f"Processing {i+1}/{len(image_files)}: {filename}")
            
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
        
        print(f"\n✅ Processing complete!")
        print(f"Successfully processed: {processed_count}")
        print(f"Failed: {failed_count}")
        print(f"Output directory: {self.output_dir}")
        print(f"Configuration file: {self.config_file}")
        print(f"Processing info: text_overlay_processing_info.json")
        
        return processing_info

def main():
    applier = TextOverlayApplier()
    info = applier.process_all_images()
    
    print("\n🎨 Text overlays applied to all images!")
    print("📝 You can edit text_overlay_config.json to adjust settings and re-run if needed.")

if __name__ == "__main__":
    main()
