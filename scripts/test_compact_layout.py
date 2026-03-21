#!/usr/bin/env python3
"""
Test Compact Layout with Badge Space
- Date centered at top
- Gap for badge
- Skater, trick, location with minimal spacing
"""

import os
from PIL import Image, ImageDraw, ImageFont

class CompactLayoutTester:
    def __init__(self):
        self.input_dir = "images/original"
        self.output_dir = "images/compact_layout_tests"
        self.lock_screen_size = (1179, 2556)  # iPhone 14 Pro Max
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Test different Y positions
        self.y_positions = [2380, 2400, 2420, 2440]
        
        # Test cover
        self.test_cover = {
            "filename": "November1991.jpg",
            "metadata": {
                "year": "1991", "month": "11",
                "skater": "eric dressen",
                "trick": "nose bonk tail grab",
                "location": "Los Angeles CA"
            }
        }
        
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
                    font_small = ImageFont.truetype(path, 44)  # Slightly smaller
                    return {"large": font_large, "medium": font_medium, "small": font_small}
        except Exception:
            pass
        default = ImageFont.load_default()
        return {"large": default, "medium": default, "small": default}
    
    def create_layout(self, y_position):
        """Create compact layout with badge space"""
        try:
            filename = self.test_cover["filename"]
            metadata = self.test_cover["metadata"]
            
            input_path = os.path.join(self.input_dir, filename)
            if not os.path.exists(input_path):
                print(f"  ⚠️  {filename} not found")
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
            text_x = 590  # Center horizontally
            
            # Layout structure:
            # 1. Date (centered, larger font)
            # 2. Gap for badge (60px)
            # 3. Skater, trick, location (compact, smaller font)
            
            # Line 1: Date
            date_text = "November 1991"
            date_font = fonts["large"]
            date_bbox = draw.textbbox((0, 0), date_text, font=date_font)
            date_height = date_bbox[3] - date_bbox[1]
            date_y = y_position + (date_height // 2)
            
            # Draw date with outline
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((text_x + dx, date_y + dy), date_text, font=date_font, 
                                 fill=outline_color, anchor="mm")
            draw.text((text_x, date_y), date_text, font=date_font, fill=text_color, anchor="mm")
            
            # Gap for badge (60px)
            current_y = y_position + date_height + 60
            
            # Lines 2-4: Skater, trick, location (compact)
            compact_lines = [
                ("skater", metadata["skater"], fonts["small"]),
                ("trick", metadata["trick"], fonts["small"]),
                ("location", metadata["location"], fonts["small"])
            ]
            
            compact_spacing = 42  # Minimal spacing
            
            for line_type, text, font in compact_lines:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_height = bbox[3] - bbox[1]
                text_y = current_y + (text_height // 2)
                
                # Draw outline
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((text_x + dx, text_y + dy), text, font=font, 
                                     fill=outline_color, anchor="mm")
                
                # Draw main text
                draw.text((text_x, text_y), text, font=font, fill=text_color, anchor="mm")
                
                current_y += text_height + compact_spacing
            
            # Save
            output_filename = f"compact_y{y_position}_November1991.jpg"
            output_path = os.path.join(self.output_dir, output_filename)
            overlay_image.save(output_path, quality=95)
            
            print(f"  ✅ Y={y_position}: {output_filename}")
            return output_path
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_tests(self):
        """Test all Y positions"""
        print("🧪 Testing Compact Layout with Badge Space")
        print("━" * 70)
        print("📱 Layout:")
        print("   1. Date (centered, large)")
        print("   2. Gap for badge (60px)")
        print("   3. Skater, trick, location (compact, 42px spacing)")
        print("━" * 70)
        print()
        
        for y_pos in self.y_positions:
            self.create_layout(y_pos)
        
        print()
        print("✅ Compact layout tests complete!")
        print(f"📁 Output: {self.output_dir}/")

if __name__ == "__main__":
    tester = CompactLayoutTester()
    tester.run_tests()



