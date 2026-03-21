#!/usr/bin/env python3
"""
Perfect Centered Layout
- Date above badge gap
- Skater/trick/location below badge gap
- ENTIRE BLOCK centered in available space
"""

import os
from PIL import Image, ImageDraw, ImageFont

class PerfectCenteredTester:
    def __init__(self):
        self.input_dir = "images/original"
        self.output_dir = "images/perfect_centered_tests"
        self.lock_screen_size = (1179, 2556)  # iPhone 14 Pro Max
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Test covers
        self.test_covers = [
            {"filename": "January1981.jpg", "lines": 1, "metadata": {"year": "1981", "month": "01"}},
            {"filename": "February1981.jpg", "lines": 2, "metadata": {"year": "1981", "month": "02", "skater": "Chris Stople"}},
            {"filename": "March1981.jpg", "lines": 3, "metadata": {"year": "1981", "month": "03", "skater": "Chris Miller", "trick": "FS Air"}},
            {"filename": "November1991.jpg", "lines": 4, "metadata": {"year": "1991", "month": "11", "skater": "eric dressen", "trick": "nose bonk tail grab", "location": "Los Angeles CA"}},
        ]
        
    def load_fonts(self):
        """Load fonts with fallback"""
        try:
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
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
    
    def create_layout(self, test_data):
        """Create perfectly centered layout"""
        try:
            filename = test_data["filename"]
            metadata = test_data["metadata"]
            expected_lines = test_data["lines"]
            
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
            
            # Available space for entire text block
            text_area_top = 2180  # Below music widget area
            text_area_bottom = 2520  # Above home swipe
            available_space = text_area_bottom - text_area_top  # 340px total
            
            # Build date line (ABOVE badge)
            month_name = self.get_month_name(int(metadata["month"]))
            date_text = f"{month_name} {metadata['year']}"
            date_font = fonts["large"]
            date_bbox = draw.textbbox((0, 0), date_text, font=date_font)
            date_height = date_bbox[3] - date_bbox[1]
            
            # Badge gap (space for floating badge)
            badge_gap = 80  # Gap for badge
            
            # Build lines BELOW badge
            below_lines = []
            if metadata.get("skater"):
                below_lines.append((metadata["skater"], fonts["large"]))
            if metadata.get("trick"):
                below_lines.append((metadata["trick"], fonts["medium"]))
            if metadata.get("location"):
                below_lines.append((metadata["location"], fonts["medium"]))
            
            # Calculate total height BELOW badge
            below_spacing = 42  # Tight spacing between bottom lines
            total_below_height = 0
            for text, font in below_lines:
                bbox = draw.textbbox((0, 0), text, font=font)
                total_below_height += (bbox[3] - bbox[1])
            if len(below_lines) > 1:
                total_below_height += (len(below_lines) - 1) * below_spacing
            
            # TOTAL height of entire text block
            total_block_height = date_height + badge_gap + total_below_height
            
            # Center the ENTIRE block in available space
            block_start_y = text_area_top + ((available_space - total_block_height) // 2)
            
            # Draw date (first part of block)
            date_y = block_start_y + (date_height // 2)
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((text_x + dx, date_y + dy), date_text, font=date_font, 
                                 fill=outline_color, anchor="mm")
            draw.text((text_x, date_y), date_text, font=date_font, fill=text_color, anchor="mm")
            
            # Skip badge gap
            current_y = block_start_y + date_height + badge_gap
            
            # Draw lines BELOW badge
            for text, font in below_lines:
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
                
                current_y += text_height + below_spacing
            
            # Save
            output_filename = f"perfect_{expected_lines}line_{filename}"
            output_path = os.path.join(self.output_dir, output_filename)
            overlay_image.save(output_path, quality=95)
            
            print(f"  ✅ {expected_lines} lines: {output_filename}")
            print(f"     Block Y: {block_start_y} to {block_start_y + total_block_height} (centered in {available_space}px)")
            return output_path
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_tests(self):
        """Test all covers"""
        print("🧪 Perfect Centered Layout")
        print("━" * 70)
        print("📱 Layout:")
        print("   1. Date (centered in its portion above badge)")
        print("   2. Badge gap (80px)")
        print("   3. Skater/trick/location (tight spacing, 42px)")
        print("   ENTIRE BLOCK centered in available space")
        print("━" * 70)
        print()
        
        for test_cover in self.test_covers:
            print(f"Testing {test_cover['lines']}-line cover: {test_cover['filename']}")
            self.create_layout(test_cover)
            print()
        
        print("✅ Perfect centered tests complete!")
        print(f"📁 Output: {self.output_dir}/")

if __name__ == "__main__":
    tester = PerfectCenteredTester()
    tester.run_tests()

