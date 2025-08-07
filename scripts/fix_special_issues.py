#!/usr/bin/env python3
"""
Fix Special Issues Script
Handles special issues like Summer and PhotoIssue by matching with 4ply CSV data
"""

import csv
import os
from PIL import Image, ImageDraw, ImageFont
import json

class SpecialIssueFixer:
    def __init__(self):
        self.input_dir = "images/optimized_final_fixed"
        self.output_dir = "images/optimized_final_with_text"
        self.csv_file = "data/4ply_covers.csv"
        self.config_file = "text_overlay_config.json"
        
        # Load configuration
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
        
        # Load 4ply data
        self.fourply_data = self.load_4ply_data()
        
        # Special issue mappings
        self.special_issue_mappings = {
            "Summer": "summer",
            "PhotoIssue": "photo"
        }
        
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
                
                # Also store by special issue type
                if row['month'].lower() in ['summer', 'winter']:
                    special_key = f"{year}_{row['month'].lower()}"
                    fourply_data[special_key] = row
        
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
    
    def find_special_issue_metadata(self, filename):
        """Find metadata for special issues"""
        name_without_ext = os.path.splitext(filename)[0]
        
        if '_' in name_without_ext:
            parts = name_without_ext.split('_')
            if len(parts) >= 2:
                year = parts[0]
                special_type = parts[1]
                
                # Try different matching strategies
                possible_keys = [
                    f"{year}_{special_type.lower()}",  # 2008_summer
                    f"{year}_summer",                   # 2008_summer
                    f"{year}_winter",                   # 2008_winter
                    f"{year}_photo",                    # 2009_photo
                ]
                
                for key in possible_keys:
                    if key in self.fourply_data:
                        metadata = self.fourply_data[key].copy()
                        metadata['year'] = year
                        metadata['month'] = self.get_special_month_number(special_type)
                        return metadata
                
                # If no exact match, create basic metadata
                return {
                    'year': year,
                    'month': self.get_special_month_number(special_type),
                    'skater': '',
                    'trick': '',
                    'location': '',
                    'notes': f"Special {special_type} issue"
                }
        
        return None
    
    def get_special_month_number(self, special_type):
        """Get month number for special issues"""
        special_months = {
            'Summer': 6,  # June
            'PhotoIssue': 9,  # September
            'Photo': 9,  # September
        }
        return special_months.get(special_type, 6)
    
    def get_month_name(self, month_num):
        """Convert month number to name"""
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return months[month_num - 1] if 1 <= month_num <= 12 else ''
    
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
    
    def fix_special_issues(self):
        """Fix special issue images"""
        print("Fixing special issue images...")
        
        # List of special issue files that failed
        special_issue_files = [
            "2008_Summer.jpg",
            "2005_Summer.jpg", 
            "2007_Summer.jpg",
            "2004_Summer.jpg",
            "2006_Summer.jpg",
            "2009_PhotoIssue.jpg",
            "2002_PhotoIssue.jpg",
            "2003_PhotoIssue.jpg"
        ]
        
        fixed_count = 0
        
        for filename in special_issue_files:
            image_path = os.path.join(self.input_dir, filename)
            
            if os.path.exists(image_path):
                print(f"Processing special issue: {filename}")
                
                # Find metadata for special issue
                metadata = self.find_special_issue_metadata(filename)
                
                if metadata:
                    # Create text overlay
                    output_path = self.create_text_overlay(image_path, metadata)
                    if output_path:
                        fixed_count += 1
                        print(f"✅ Fixed: {filename}")
                        print(f"   Metadata: {metadata.get('skater', 'N/A')} - {metadata.get('trick', 'N/A')}")
                    else:
                        print(f"❌ Failed to process: {filename}")
                else:
                    print(f"❌ No metadata found for: {filename}")
            else:
                print(f"❌ File not found: {filename}")
        
        print(f"\n✅ Fixed {fixed_count} special issue images!")
        return fixed_count

def main():
    fixer = SpecialIssueFixer()
    fixed_count = fixer.fix_special_issues()
    
    print(f"\n🎨 Special issues fixed! Total images with text overlays should now be {542 + fixed_count}")

if __name__ == "__main__":
    main()
