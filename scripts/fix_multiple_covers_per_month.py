#!/usr/bin/env python3
"""
Fix Multiple Covers Per Month Script
Handles months with multiple covers by creating proper mappings
"""

import csv
import os
from PIL import Image, ImageDraw, ImageFont
import json
from collections import defaultdict

class MultipleCoversFixer:
    def __init__(self):
        self.input_dir = "images/optimized_final_fixed"
        self.output_dir = "images/optimized_final_with_text"
        self.csv_file = "data/4ply_covers.csv"
        self.config_file = "text_overlay_config.json"
        self.lock_screen_size = (1179, 2556)  # iPhone 14 Pro Max
        
        # Load configuration
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
        
        # Load 4ply data with multiple covers support
        self.fourply_data, self.multiple_covers = self.load_4ply_data_with_multiples()
        
    def load_4ply_data_with_multiples(self):
        """Load 4ply CSV data and identify months with multiple covers"""
        fourply_data = {}
        monthly_counts = defaultdict(list)
        
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                year = row['year']
                month = self.month_to_number(row['month'])
                if month:
                    key = f"{year}_{month:02d}"
                    monthly_counts[key].append(row)
        
        # Create mappings for multiple covers
        multiple_covers = {}
        for key, covers in monthly_counts.items():
            if len(covers) > 1:
                multiple_covers[key] = covers
                print(f"Found {len(covers)} covers for {key}:")
                for i, cover in enumerate(covers):
                    skater = cover.get('skater', 'Unknown')
                    trick = cover.get('trick', 'Unknown')
                    detail = cover.get('detailer', cover.get('special', ''))
                    print(f"  {i+1}. {skater} - {trick} ({detail})")
                    
                    # Store each cover with index
                    if i == 0:
                        fourply_data[key] = cover  # First cover gets base key
                    else:
                        fourply_data[f"{key}_{i:02d}"] = cover  # Additional covers get indexed keys
            else:
                fourply_data[key] = covers[0]
        
        print(f"\nLoaded {len(fourply_data)} entries from 4ply CSV")
        print(f"Found {len(multiple_covers)} months with multiple covers")
        
        return fourply_data, multiple_covers
    
    def month_to_number(self, month_name):
        """Convert month name to number"""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'winter': 12  # Winter issue typically December
        }
        return months.get(month_name.lower())
    
    def analyze_existing_images(self):
        """Analyze what images we have vs what data is available"""
        print("\n🔍 ANALYSIS: Image Files vs CSV Data")
        print("="*50)
        
        for key, covers in self.multiple_covers.items():
            year, month = key.split('_')
            print(f"\n📅 {year}-{month} ({len(covers)} covers in CSV):")
            
            # Check what image files exist
            base_pattern = f"{key}.jpg"
            indexed_patterns = [f"{key}_{i:02d}.jpg" for i in range(1, len(covers))]
            
            existing_files = []
            for pattern in [base_pattern] + indexed_patterns:
                image_path = os.path.join(self.input_dir, pattern)
                if os.path.exists(image_path):
                    existing_files.append(pattern)
            
            print(f"  📁 Image files found: {existing_files}")
            
            # Show available data
            for i, cover in enumerate(covers):
                skater = cover.get('skater', 'Unknown')
                trick = cover.get('trick', 'Unknown')
                special = cover.get('special', '')
                detailer = cover.get('detailer', '')
                identifier = special if special else detailer
                print(f"  📊 Data {i+1}: {skater} - {trick} ({identifier})")
    
    def create_mapping_suggestions(self):
        """Create suggestions for mapping images to correct data"""
        print("\n💡 MAPPING SUGGESTIONS")
        print("="*50)
        
        suggestions = {}
        
        for key, covers in self.multiple_covers.items():
            year, month = key.split('_')
            
            # Check what files exist
            existing_files = []
            for i in range(len(covers)):
                if i == 0:
                    pattern = f"{key}.jpg"
                else:
                    pattern = f"{key}_{i:02d}.jpg"
                    
                if os.path.exists(os.path.join(self.input_dir, pattern)):
                    existing_files.append((pattern, i))
            
            if existing_files:
                suggestions[key] = {
                    'covers_data': covers,
                    'image_files': existing_files
                }
                
                print(f"\n📅 {year}-{month}:")
                for filename, data_index in existing_files:
                    cover = covers[data_index] if data_index < len(covers) else covers[0]
                    skater = cover.get('skater', 'Unknown')
                    trick = cover.get('trick', 'Unknown')
                    special = cover.get('special', '')
                    print(f"  {filename} → {skater} - {trick} ({special})")
        
        return suggestions
    
    def create_text_overlay(self, image_path, metadata):
        """Create text overlay on image using the configuration"""
        try:
            # Load image
            with Image.open(image_path) as image:
                image = image.copy()
                
            # Create drawing context
            draw = ImageDraw.Draw(image)
            
            # Load fonts
            try:
                large_font = ImageFont.truetype(f"{self.config['font_settings']['font_family']}.ttf", 
                                              self.config['font_settings']['large_size'])
                medium_font = ImageFont.truetype(f"{self.config['font_settings']['font_family']}.ttf", 
                                               self.config['font_settings']['medium_size'])
                small_font = ImageFont.truetype(f"{self.config['font_settings']['font_family']}.ttf", 
                                              self.config['font_settings']['small_size'])
            except:
                # Fallback to default font
                large_font = ImageFont.load_default()
                medium_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Build text lines based on configuration
            text_lines = []
            
            if self.config['content']['show_date']:
                year = metadata.get('year', '')
                month = metadata.get('month', '')
                if year and month:
                    month_name = self.get_month_name(int(month))
                    date_text = f"{month_name} {year}"
                    text_lines.append((date_text, large_font))
            
            if self.config['content']['show_skater'] and metadata.get('skater'):
                skater = metadata.get('skater', '').title()
                text_lines.append((skater, medium_font))
            
            if self.config['content']['show_trick'] and metadata.get('trick'):
                trick = metadata.get('trick', '').title()
                text_lines.append((trick, small_font))
            
            if self.config['content']['show_location'] and metadata.get('location'):
                location = metadata.get('location', '')
                text_lines.append((location, small_font))
            
            if self.config['content']['show_obstacle'] and metadata.get('obstacle'):
                obstacle = metadata.get('obstacle', '').title()
                text_lines.append((obstacle, small_font))
            
            # Draw text lines
            y_position = self.config['positioning']['text_y_start']
            text_color = tuple(self.config['colors']['text_color'])
            outline_color = tuple(self.config['colors']['outline_color'])
            outline_width = self.config['colors']['outline_width']
            
            for text, font in text_lines:
                if text.strip():  # Only draw non-empty text
                    x_position = self.config['positioning']['text_x']
                    
                    # Draw text with outline
                    for dx in range(-outline_width, outline_width + 1):
                        for dy in range(-outline_width, outline_width + 1):
                            if dx != 0 or dy != 0:
                                draw.text((x_position + dx, y_position + dy), text, 
                                        font=font, fill=outline_color)
                    
                    # Draw main text
                    draw.text((x_position, y_position), text, font=font, fill=text_color)
                    
                    y_position += self.config['positioning']['line_spacing']
            
            # Save image
            output_filename = os.path.basename(image_path)
            output_path = os.path.join(self.output_dir, output_filename)
            image.save(output_path, 'JPEG', quality=95)
            
            return output_path
            
        except Exception as e:
            print(f"Error creating text overlay for {image_path}: {e}")
            return None
    
    def get_month_name(self, month_num):
        """Convert month number to name"""
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        return months[month_num] if 1 <= month_num <= 12 else ''
    
    def apply_fixes(self, manual_mappings=None):
        """Apply fixes based on mappings"""
        if not manual_mappings:
            print("⚠️ No manual mappings provided. Using automatic suggestions.")
            return
        
        print("\n🔧 APPLYING FIXES")
        print("="*30)
        
        fixed_count = 0
        
        for image_file, data_key in manual_mappings.items():
            image_path = os.path.join(self.input_dir, image_file)
            if not os.path.exists(image_path):
                print(f"❌ Image not found: {image_file}")
                continue
            
            # Get metadata
            metadata = self.fourply_data.get(data_key, {})
            if not metadata:
                print(f"❌ No data found for key: {data_key}")
                continue
            
            # Extract year/month from filename for metadata
            name_parts = os.path.splitext(image_file)[0].split('_')
            if len(name_parts) >= 2:
                metadata['year'] = name_parts[0]
                metadata['month'] = name_parts[1]
            
            # Apply text overlay
            output_path = self.create_text_overlay(image_path, metadata)
            if output_path:
                skater = metadata.get('skater', 'Unknown')
                trick = metadata.get('trick', 'Unknown')
                print(f"✅ Fixed {image_file} → {skater} - {trick}")
                fixed_count += 1
            else:
                print(f"❌ Failed to process {image_file}")
        
        print(f"\n🎉 Fixed {fixed_count} images!")
        return fixed_count

def main():
    fixer = MultipleCoversFixer()
    
    print("🔍 Analyzing multiple covers per month...")
    fixer.analyze_existing_images()
    
    print("\n💡 Creating mapping suggestions...")
    suggestions = fixer.create_mapping_suggestions()
    
    print("\n" + "="*60)
    print("📋 RECOMMENDED MANUAL MAPPINGS")
    print("="*60)
    print("""
Based on the analysis, here are the recommended manual mappings:

# January 2013 - 5 covers available
manual_mappings = {
    "2013_01.jpg": "2013_01",        # Stevie Perez (current - already correct)
    "2013_01_01.jpg": "2013_01_01",  # Vincent Alvarez  
    "2013_01_02.jpg": "2013_01_02",  # Elijah Berle
    "2013_01_03.jpg": "2013_01_03",  # Corey Kennedy
    "2013_01_04.jpg": "2013_01_04",  # Raven Tershy
}

To apply these fixes, run:
fixer.apply_fixes(manual_mappings)
    """)

if __name__ == "__main__":
    main()
