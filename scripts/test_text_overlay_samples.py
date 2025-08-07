#!/usr/bin/env python3
"""
Test Text Overlay Samples Script
Creates a few sample images with text overlays using 4ply CSV data
for testing font, size, and positioning before applying to all images
"""

import csv
import os
from PIL import Image, ImageDraw, ImageFont
import json

class TextOverlayTester:
    def __init__(self):
        self.input_dir = "images/optimized_final_fixed"
        self.output_dir = "images/text_overlay_samples"
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
    
    def create_text_overlay(self, image_path, metadata, sample_num):
        """Create text overlay on image"""
        try:
            # Open image
            image = Image.open(image_path)
            
            # Create a copy for drawing
            overlay_image = image.copy()
            draw = ImageDraw.Draw(overlay_image)
            
            # Try to load Roboto font, fallback to default
            try:
                font_large = ImageFont.truetype("Roboto-Bold.ttf", 56)
                font_medium = ImageFont.truetype("Roboto-Regular.ttf", 48)
                font_small = ImageFont.truetype("Roboto-Regular.ttf", 40)
            except:
                # Fallback fonts
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Text color (white)
            text_color = (255, 255, 255)
            
            # Position for text (centered horizontally, positioned between flashlight and camera)
            text_x = 590  # Center horizontally
            text_y_start = 2200  # Start position
            
            # Build text content
            lines = []
            
            # Date line
            if metadata.get('year') and metadata.get('month'):
                month_name = self.get_month_name(int(metadata['month']))
                date_text = f"{month_name} {metadata['year']}"
                lines.append(date_text)
            
            # Skater line
            if metadata.get('skater') and metadata['skater'].strip():
                skater_text = metadata['skater'].strip()
                lines.append(skater_text)
            
            # Trick line
            if metadata.get('trick') and metadata['trick'].strip():
                trick_text = metadata['trick'].strip()
                lines.append(trick_text)
            
            # Location line
            if metadata.get('location') and metadata['location'].strip():
                location_text = metadata['location'].strip()
                lines.append(location_text)
            
            # Draw text lines
            line_spacing = 70
            for i, line in enumerate(lines):
                # Choose font based on line type
                if i == 0:  # Date - largest
                    font = font_large
                elif i == 1:  # Skater - large
                    font = font_large
                else:  # Other info - medium
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
                
                # Draw text with black outline for better visibility
                outline_color = (0, 0, 0)
                outline_width = 3
                
                # Draw outline
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        draw.text((x + dx, y + dy), line, font=font, fill=outline_color)
                
                # Draw main text
                draw.text((x, y), line, font=font, fill=text_color)
            
            # Save the image
            filename = os.path.basename(image_path)
            output_path = os.path.join(self.output_dir, f"sample_{sample_num}_{filename}")
            overlay_image.save(output_path, quality=95)
            
            print(f"Created sample {sample_num}: {filename}")
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
    
    def create_samples(self, num_samples=5):
        """Create sample text overlay images"""
        print(f"Creating {num_samples} sample text overlay images...")
        
        # Get list of available images
        image_files = []
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(filename)
        
        print(f"Found {len(image_files)} images to choose from")
        
        # Create samples
        created_samples = []
        
        for i in range(min(num_samples, len(image_files))):
            filename = image_files[i]
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
                    output_path = self.create_text_overlay(image_path, metadata, i + 1)
                    if output_path:
                        created_samples.append({
                            'input': filename,
                            'output': os.path.basename(output_path),
                            'metadata': metadata
                        })
        
        # Save sample info
        sample_info = {
            'samples_created': len(created_samples),
            'samples': created_samples
        }
        
        with open('text_overlay_samples_info.json', 'w') as f:
            json.dump(sample_info, f, indent=2)
        
        print(f"\n✅ Created {len(created_samples)} sample images in {self.output_dir}/")
        print("📝 Sample info saved to text_overlay_samples_info.json")
        
        return created_samples

def main():
    tester = TextOverlayTester()
    samples = tester.create_samples(5)
    
    print("\n🎨 Sample images created! Check the images/text_overlay_samples/ directory")
    print("You can now review the font, size, and positioning before we apply to all images.")

if __name__ == "__main__":
    main()
