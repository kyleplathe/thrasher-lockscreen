#!/usr/bin/env python3
"""
Create Test Sample Images
Generates 4 test images with 1, 2, 3, and 4 lines of text to check alignment
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont

class TestSampleCreator:
    def __init__(self):
        self.input_dir = "images/original"
        self.output_dir = "images/archive/test_samples"
        self.lock_screen_size = (1179, 2556)  # iPhone 14 Pro Max
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Test samples: filename, metadata
        self.test_samples = [
            {
                "filename": "January1981.jpg",
                "metadata": {
                    "year": "1981", "month": "01", 
                    "skater": None, "trick": None, "location": None
                },
                "expected_lines": 1
            },
            {
                "filename": "February1981.jpg",
                "metadata": {
                    "year": "1981", "month": "02", 
                    "skater": "Chris Stople", "trick": None, "location": None
                },
                "expected_lines": 2
            },
            {
                "filename": "March1981.jpg",
                "metadata": {
                    "year": "1981", "month": "03", 
                    "skater": "Chris Miller", "trick": "FS Air", "location": None
                },
                "expected_lines": 3
            },
            {
                "filename": "May1981.jpg",
                "metadata": {
                    "year": "1981", "month": "05", 
                    "skater": "Steve Caballero", "trick": "Lien Air", "location": "Whittier"
                },
                "expected_lines": 4
            }
        ]
        
    def load_fonts(self):
        """Load fonts with fallback"""
        try:
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf",  # Linux
                "C:/Windows/Fonts/arial.ttf",  # Windows
            ]
            
            for path in font_paths:
                if os.path.exists(path):
                    font_large = ImageFont.truetype(path, 56)
                    font_medium = ImageFont.truetype(path, 48)
                    return {"large": font_large, "medium": font_medium}
                    
        except Exception:
            pass
            
        # Fallback
        default = ImageFont.load_default()
        return {"large": default, "medium": default}
    
    def get_month_name(self, month_num):
        """Convert month number to name"""
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        return months[month_num - 1] if 1 <= month_num <= 12 else ''
    
    def create_sample(self, test_sample):
        """Create a test sample image with current alignment"""
        try:
            filename = test_sample["filename"]
            metadata = test_sample["metadata"]
            expected_lines = test_sample["expected_lines"]
            
            input_path = os.path.join(self.input_dir, filename)
            if not os.path.exists(input_path):
                print(f"  ⚠️  Image not found: {filename}")
                return None
            
            # Open image
            image = Image.open(input_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create a new image with lock screen dimensions and black background
            lock_screen_image = Image.new('RGB', self.lock_screen_size, (0, 0, 0))
            
            # Calculate scaling to fit the entire magazine cover
            img_ratio = image.width / image.height
            target_ratio = self.lock_screen_size[0] / self.lock_screen_size[1]
            
            # Scale image to fit within lock screen while maintaining aspect ratio
            if img_ratio > target_ratio:
                # Image is wider than target - scale to fit width
                scale_factor = self.lock_screen_size[0] / image.width
                new_width = self.lock_screen_size[0]
                new_height = int(image.height * scale_factor)
            else:
                # Image is taller than target - scale to fit height
                scale_factor = self.lock_screen_size[1] / image.height
                new_width = int(image.width * scale_factor)
                new_height = self.lock_screen_size[1]
            
            # Resize the magazine cover
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Calculate position to center the image
            x_offset = (self.lock_screen_size[0] - new_width) // 2
            y_offset = (self.lock_screen_size[1] - new_height) // 2
            
            # Paste the resized magazine cover onto the lock screen background
            lock_screen_image.paste(resized_image, (x_offset, y_offset))
            
            # Use the lock screen image for drawing
            overlay_image = lock_screen_image
            draw = ImageDraw.Draw(overlay_image)
            
            # Load fonts
            fonts = self.load_fonts()
            
            # Colors
            text_color = (255, 255, 255)  # White
            outline_color = (0, 0, 0)     # Black
            outline_width = 3
            
            # Positioning from config
            text_x = 590  # Center horizontally (1179/2)
            text_y_start = 2350  # Start position
            line_spacing = 70
            
            # Build text lines
            lines = []
            if metadata.get("month") and metadata.get("year"):
                month_name = self.get_month_name(int(metadata["month"]))
                lines.append(("date", f"{month_name} {metadata['year']}", fonts["large"]))
            
            if metadata.get("skater"):
                lines.append(("skater", metadata["skater"], fonts["large"]))
            
            if metadata.get("trick"):
                lines.append(("trick", metadata["trick"], fonts["medium"]))
            
            if metadata.get("location"):
                lines.append(("location", metadata["location"], fonts["medium"]))
            
            # CURRENT METHOD: Draw lines with fixed spacing
            for i, (line_type, text, font) in enumerate(lines):
                text_y = text_y_start + (i * line_spacing)
                
                # Get text bounds for centering
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Center the text horizontally
                x = text_x - (text_width // 2)
                y = text_y - (text_height // 2)
                
                # Draw outline
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
                
                # Draw main text
                draw.text((x, y), text, font=font, fill=text_color)
            
            # Save
            output_filename = f"sample_{expected_lines}line_{filename}"
            output_path = os.path.join(self.output_dir, output_filename)
            overlay_image.save(output_path, quality=95)
            
            print(f"  ✅ Created: {output_filename} ({len(lines)} lines)")
            return output_path
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def run(self):
        """Create all test samples"""
        print("🎨 Creating Test Sample Images")
        print("━" * 60)
        print(f"📱 Screen: {self.lock_screen_size[0]}x{self.lock_screen_size[1]} (iPhone 14 Pro Max)")
        print(f"📍 Text position: Y={text_y_start}")
        print(f"📏 Line spacing: {line_spacing}px")
        print("━" * 60)
        print()
        
        for sample in self.test_samples:
            print(f"Creating {sample['expected_lines']}-line sample: {sample['filename']}")
            self.create_sample(sample)
        
        print()
        print("✅ Test samples complete!")
        print(f"📁 Output directory: {self.output_dir}/")

if __name__ == "__main__":
    # Fix undefined variable
    text_y_start = 2350
    line_spacing = 70
    
    creator = TestSampleCreator()
    creator.run()

