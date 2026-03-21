#!/usr/bin/env python3
"""
Test Different Text Positions
Creates samples with text at different Y positions to find optimal placement
"""

import os
from PIL import Image, ImageDraw, ImageFont

class PositionTester:
    def __init__(self):
        self.input_dir = "images/original"
        self.output_dir = "images/archive/position_tests"
        self.lock_screen_size = (1179, 2556)  # iPhone 14 Pro Max
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Test different Y positions (lower = closer to bottom)
        # Screen is 2556px tall, home swipe around 2440-2500
        self.test_positions = [
            2400,  # Current position (too high?)
            2420,  # A bit lower
            2440,  # Mid position
            2460,  # Lower position
        ]
        
        # Test samples
        self.test_covers = [
            {"filename": "January1981.jpg", "lines": 1},
            {"filename": "February1981.jpg", "lines": 2, "skater": "Chris Stople"},
            {"filename": "March1981.jpg", "lines": 3, "skater": "Chris Miller", "trick": "FS Air"},
            {"filename": "May1981.jpg", "lines": 4, "skater": "Steve Caballero", "trick": "Lien Air", "location": "Whittier"},
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
            
        default = ImageFont.load_default()
        return {"large": default, "medium": default}
    
    def get_month_name(self, month_num):
        """Convert month number to name"""
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        return months[month_num - 1] if 1 <= month_num <= 12 else ''
    
    def create_sample(self, filename, y_position, test_info):
        """Create a test sample with specific Y position"""
        try:
            input_path = os.path.join(self.input_dir, filename)
            if not os.path.exists(input_path):
                return None
            
            # Open and format image
            image = Image.open(input_path)
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
            
            # Build text lines
            lines = []
            name_parts = os.path.splitext(filename)[0].replace("1981", "")
            month_name = name_parts
            lines.append(("date", f"{month_name} 1981", fonts["large"]))
            
            if test_info.get("skater"):
                lines.append(("skater", test_info["skater"], fonts["large"]))
            
            if test_info.get("trick"):
                lines.append(("trick", test_info["trick"], fonts["medium"]))
            
            if test_info.get("location"):
                lines.append(("location", test_info["location"], fonts["medium"]))
            
            # Draw text at specified Y position
            line_spacing = 70
            for i, (line_type, text, font) in enumerate(lines):
                text_y = y_position + (i * line_spacing)
                
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = 590 - (text_width // 2)
                y = text_y - (text_height // 2)
                
                # Draw outline
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
                
                # Draw main text
                draw.text((x, y), text, font=font, fill=text_color)
            
            # Save
            output_filename = f"y{y_position}_{test_info['lines']}line_{os.path.basename(filename)}"
            output_path = os.path.join(self.output_dir, output_filename)
            overlay_image.save(output_path, quality=95)
            
            print(f"  ✅ Y={y_position}: {output_filename}")
            return output_path
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def run_tests(self):
        """Test all positions"""
        print("🧪 Testing Different Text Y-Positions")
        print("━" * 70)
        print(f"📱 Screen height: {self.lock_screen_size[1]}px")
        print(f"📍 Home swipe: ~2440-2500px from top")
        print(f"🗂️  Testing {len(self.test_positions)} positions")
        print("━" * 70)
        print()
        
        for test_cover in self.test_covers:
            print(f"Testing {test_cover['lines']}-line cover: {test_cover['filename']}")
            for y_pos in self.test_positions:
                self.create_sample(test_cover['filename'], y_pos, test_cover)
            print()
        
        print("✅ Position tests complete!")
        print(f"📁 Output: {self.output_dir}/")

if __name__ == "__main__":
    tester = PositionTester()
    tester.run_tests()



